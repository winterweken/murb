import tempfile
from pathlib import Path

import pandas as pd
import pvlib.iotools
import streamlit as st

from webapp import form_defaults, report, runner

st.set_page_config(page_title="murb energy tool", layout="wide")
st.title("murb energy tool")
st.caption("Early-stage energy modelling for Canadian buildings. Upload an EPW weather file, fill in the form, and run.")


def _validate_epw(epw_bytes: bytes, filename: str):
    with tempfile.NamedTemporaryFile(suffix=".epw", delete=True) as tmp:
        tmp.write(epw_bytes)
        tmp.flush()
        _, metadata = pvlib.iotools.read_epw(tmp.name, coerce_year=2021)
    return metadata


# --- Sidebar: identification + EPW upload + run button ---
with st.sidebar:
    st.header("Run")
    name = st.text_input("Run name", value="Test Building")
    province = st.selectbox("Province", form_defaults.PROVINCES, index=form_defaults.PROVINCES.index("AB"))

    st.divider()
    st.subheader("Weather (EPW)")
    epw_upload = st.file_uploader("Upload an EPW file", type=["epw"])

    if epw_upload is not None:
        if epw_upload.size > 10 * 1024 * 1024:
            st.error(f"File too large ({epw_upload.size / 1e6:.1f} MB). EPW files are typically 1–3 MB.")
        else:
            epw_bytes = epw_upload.getvalue()
            try:
                metadata = _validate_epw(epw_bytes, epw_upload.name)
            except Exception as e:
                st.error(f"Could not parse EPW: {e}")
            else:
                st.session_state["epw_bytes"] = epw_bytes
                st.session_state["epw_filename"] = epw_upload.name
                st.session_state["epw_metadata"] = metadata
                st.success(
                    f"Loaded **{metadata.get('city', 'Unknown')}** — "
                    f"lat {metadata['latitude']:.2f}, lon {metadata['longitude']:.2f}, "
                    f"elev {metadata['altitude']:.0f} m"
                )
    elif "epw_metadata" in st.session_state:
        md = st.session_state["epw_metadata"]
        st.info(
            f"Using **{md.get('city', 'Unknown')}** "
            f"({st.session_state['epw_filename']})"
        )

    st.divider()
    run_clicked_placeholder = st.empty()


# --- Main pane: form ---
def _number_inputs(fields, prefix):
    values = {}
    for key, label, default, step, fmt in fields:
        values[key] = st.number_input(
            label,
            value=float(default),
            min_value=0.0,
            step=step,
            format=fmt,
            key=f"{prefix}_{key}",
        )
    return values


col_geom, col_windows = st.columns(2)

with col_geom:
    with st.expander("Geometry", expanded=True):
        geometry = _number_inputs(form_defaults.GEOMETRY_FIELDS, "geom")

with col_windows:
    with st.expander("Window groups", expanded=True):
        st.caption(
            "Add a row per orientation. `pct_window_area` should sum to 1.0. "
            "Azimuth: 0=N, 90=E, 180=S, 270=W."
        )
        default_df = pd.DataFrame(form_defaults.WINDOW_GROUP_DEFAULTS)
        window_df = st.data_editor(
            default_df,
            num_rows="dynamic",
            column_config={
                "pct_window_area": st.column_config.NumberColumn(min_value=0.0, max_value=1.0, step=0.05, format="%.2f"),
                "window_azimuth": st.column_config.NumberColumn(min_value=0, max_value=360, step=5, format="%d"),
                "shgc": st.column_config.NumberColumn(min_value=0.0, max_value=1.0, step=0.01, format="%.2f"),
                "shading": st.column_config.NumberColumn(min_value=0.0, max_value=1.0, step=0.01, format="%.2f"),
            },
            use_container_width=True,
            key="windows_editor",
        )
        pct_sum = float(window_df["pct_window_area"].fillna(0).sum())
        if abs(pct_sum - 1.0) > 1e-6:
            st.warning(f"`pct_window_area` currently sums to {pct_sum:.2f}, not 1.0.")

with st.expander("Envelope U-values"):
    envelope = _number_inputs(form_defaults.ENVELOPE_FIELDS, "env")

with st.expander("HVAC and setpoints"):
    hvac = _number_inputs(form_defaults.HVAC_FIELDS, "hvac")

with st.expander("Air leakage"):
    leakage = _number_inputs(form_defaults.LEAKAGE_FIELDS, "leak")

with st.expander("Advanced (occupancy, internal loads, thermal mass)"):
    advanced = _number_inputs(form_defaults.ADVANCED_FIELDS, "adv")
    mass_level = st.selectbox("Thermal mass level", form_defaults.MASS_LEVELS, index=1)


# --- Run gating ---
required_geometry_ok = all(geometry[k] > 0 for k in ("gfa", "area_walls_ag", "area_windows", "area_roof"))
window_rows = window_df.dropna(subset=["pct_window_area", "window_azimuth"]).to_dict("records")
window_rows = [
    {
        "pct_window_area": float(r["pct_window_area"]),
        "window_azimuth": int(r["window_azimuth"]),
        "shgc": float(r.get("shgc") if r.get("shgc") is not None else 0.4),
        "shading": float(r.get("shading") if r.get("shading") is not None else 0.0),
    }
    for r in window_rows
    if r.get("pct_window_area") is not None and float(r["pct_window_area"]) > 0
]
windows_ok = len(window_rows) > 0
epw_ok = "epw_bytes" in st.session_state
name_ok = bool(name.strip())

run_disabled = not (epw_ok and name_ok and required_geometry_ok and windows_ok)
disabled_reasons = []
if not epw_ok:
    disabled_reasons.append("upload an EPW file")
if not name_ok:
    disabled_reasons.append("set a run name")
if not required_geometry_ok:
    disabled_reasons.append("set gfa, area_walls_ag, area_windows, area_roof > 0")
if not windows_ok:
    disabled_reasons.append("add at least one window group with pct_window_area > 0")

run_help = "Ready to run." if not run_disabled else "To enable: " + "; ".join(disabled_reasons) + "."

with run_clicked_placeholder:
    run_clicked = st.button(
        "Run simulation",
        type="primary",
        disabled=run_disabled,
        help=run_help,
        use_container_width=True,
    )


if run_clicked:
    run_kwargs = {
        "name": name.strip(),
        "province": province,
        **geometry,
        **envelope,
        **hvac,
        **leakage,
        **advanced,
        "mass_level": mass_level,
    }
    with st.spinner("Running simulation..."):
        try:
            result = runner.run_simulation(
                epw_bytes=st.session_state["epw_bytes"],
                epw_filename=st.session_state["epw_filename"],
                run_kwargs=run_kwargs,
                window_groups=window_rows,
            )
        except Exception as e:
            st.error(f"Simulation failed: {e}")
            with st.expander("Traceback"):
                st.exception(e)
        else:
            st.session_state["result"] = result


if "result" in st.session_state:
    result = st.session_state["result"]
    st.divider()
    st.subheader(f"Results — {result['name']}")
    inlined = report.inline_report(result["html"], result["tables_js"], result["metadata_js"])
    st.components.v1.html(inlined, height=2000, scrolling=True)
    st.download_button(
        "Download report (zip)",
        data=report.bundle_zip(result["name"], result["html"], result["tables_js"], result["metadata_js"]),
        file_name=f"{result['name']}.zip",
        mime="application/zip",
    )
