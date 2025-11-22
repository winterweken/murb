document.getElementById('inputs').innerHTML = `
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Value</th>
      <th>Unit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Floor Area</th>
      <td>18279</td>
      <td>m2</td>
    </tr>
    <tr>
      <th>Walls Area</th>
      <td>4389.0</td>
      <td>m2</td>
    </tr>
    <tr>
      <th>Roof Area</th>
      <td>5080</td>
      <td>m2</td>
    </tr>
    <tr>
      <th>Weather File</th>
      <td>CALGARY INTL A</td>
      <td></td>
    </tr>
    <tr>
      <th>Operating Hours</th>
      <td>Custom</td>
      <td></td>
    </tr>
    <tr>
      <th>Occupancy</th>
      <td>8</td>
      <td>m2/person</td>
    </tr>
    <tr>
      <th>Plug Loads</th>
      <td>1</td>
      <td>W/m2</td>
    </tr>
    <tr>
      <th>People Outdoor Air</th>
      <td>2.5</td>
      <td>L/s/person</td>
    </tr>
    <tr>
      <th>Area Outdoor Air</th>
      <td>0.3</td>
      <td>L/s/m2</td>
    </tr>
    <tr>
      <th>Infiltration</th>
      <td>2</td>
      <td>L/s/m2 exterior area @ 75 Pa</td>
    </tr>
    <tr>
      <th>Wall R-value</th>
      <td>27.0</td>
      <td>hr ft2 F/Btu</td>
    </tr>
    <tr>
      <th>Roof R-value</th>
      <td>41.1</td>
      <td>hr ft2 F/Btu</td>
    </tr>
    <tr>
      <th>Window U-value</th>
      <td>1.9</td>
      <td>W/m2K</td>
    </tr>
    <tr>
      <th>Window SHGC</th>
      <td>[0.4, 0.4, 0.4, 0.4]</td>
      <td></td>
    </tr>
    <tr>
      <th>Shading</th>
      <td>[0.05, 0.05, 0.5, 0.5]</td>
      <td>%</td>
    </tr>
    <tr>
      <th>Lighting</th>
      <td>12.7</td>
      <td>W/m2</td>
    </tr>
    <tr>
      <th>Heat Recovery</th>
      <td>55.0</td>
      <td>%</td>
    </tr>
    <tr>
      <th>Cooling</th>
      <td>5.2</td>
      <td>COP</td>
    </tr>
    <tr>
      <th>Heating</th>
      <td>0.85</td>
      <td>COP</td>
    </tr>
    <tr>
      <th>DHW Load</th>
      <td>30</td>
      <td>W/person</td>
    </tr>
    <tr>
      <th>DHW Plant</th>
      <td>0.85</td>
      <td>COP</td>
    </tr>
    <tr>
      <th>GHG Intensity - Electricity</th>
      <td>0.69</td>
      <td>kgCO2e/kWh</td>
    </tr>
    <tr>
      <th>GHG Intensity - Natural Gas</th>
      <td>0.19</td>
      <td>kgCO2e/kWh</td>
    </tr>
  </tbody>
</table>`;
document.getElementById('annual_intensities').innerHTML = `
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>TEDI heating (kWh/m2)</th>
      <th>TEDI cooling (kWh/m2)</th>
      <th>TEUI (kWh/m2)</th>
      <th>GHGI (kgCO2e/m2)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Annual</th>
      <td>47.4</td>
      <td>10.1</td>
      <td>116.5</td>
      <td>50.5</td>
    </tr>
  </tbody>
</table>`;
document.getElementById('annual_thermal_breakdown').innerHTML = `
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Transmission</th>
      <th>Ventilation</th>
      <th>Infiltration</th>
      <th>Internal Gains</th>
      <th>Solar Gains</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Heating (kWh/m2)</th>
      <td>35.8</td>
      <td>55.5</td>
      <td>40.5</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>Cooling (kWh/m2)</th>
      <td>0.1</td>
      <td>0.2</td>
      <td>0.2</td>
      <td>2.0</td>
      <td>7.65</td>
    </tr>
  </tbody>
</table>`;
document.getElementById('monthly_thermal_demand').innerHTML = `
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Heating (kWh)</th>
      <th>Cooling (kWh)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>January</th>
      <td>190740</td>
      <td>0</td>
    </tr>
    <tr>
      <th>February</th>
      <td>171125</td>
      <td>60</td>
    </tr>
    <tr>
      <th>March</th>
      <td>98808</td>
      <td>1145</td>
    </tr>
    <tr>
      <th>April</th>
      <td>35048</td>
      <td>4734</td>
    </tr>
    <tr>
      <th>May</th>
      <td>0</td>
      <td>11190</td>
    </tr>
    <tr>
      <th>June</th>
      <td>0</td>
      <td>31711</td>
    </tr>
    <tr>
      <th>July</th>
      <td>0</td>
      <td>64564</td>
    </tr>
    <tr>
      <th>August</th>
      <td>0</td>
      <td>59293</td>
    </tr>
    <tr>
      <th>September</th>
      <td>0</td>
      <td>10725</td>
    </tr>
    <tr>
      <th>October</th>
      <td>32588</td>
      <td>1623</td>
    </tr>
    <tr>
      <th>November</th>
      <td>128495</td>
      <td>85</td>
    </tr>
    <tr>
      <th>December</th>
      <td>209462</td>
      <td>0</td>
    </tr>
  </tbody>
</table>`;
document.getElementById('annual_end_use_breakdown').innerHTML = `
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Lighting</th>
      <th>Space Heating</th>
      <th>Space Cooling</th>
      <th>Service Water Heating</th>
      <th>Plug Loads</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Annual (kWh/m2)</th>
      <td>51.0</td>
      <td>55.8</td>
      <td>1.9</td>
      <td>3.8</td>
      <td>4.0</td>
    </tr>
  </tbody>
</table>`;
document.getElementById('monthly_end_use').innerHTML = `
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Lighting (kWh)</th>
      <th>Space Heating (kWh)</th>
      <th>Space Cooling (kWh)</th>
      <th>Service Water Heating (kWh)</th>
      <th>Plug Loads (kWh)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>January</th>
      <td>79206</td>
      <td>224400</td>
      <td>0</td>
      <td>5913</td>
      <td>6236</td>
    </tr>
    <tr>
      <th>February</th>
      <td>71541</td>
      <td>201324</td>
      <td>11</td>
      <td>5341</td>
      <td>5633</td>
    </tr>
    <tr>
      <th>March</th>
      <td>79206</td>
      <td>116245</td>
      <td>220</td>
      <td>5913</td>
      <td>6236</td>
    </tr>
    <tr>
      <th>April</th>
      <td>76651</td>
      <td>41234</td>
      <td>910</td>
      <td>5722</td>
      <td>6035</td>
    </tr>
    <tr>
      <th>May</th>
      <td>79206</td>
      <td>0</td>
      <td>2151</td>
      <td>5913</td>
      <td>6236</td>
    </tr>
    <tr>
      <th>June</th>
      <td>76651</td>
      <td>0</td>
      <td>6098</td>
      <td>5722</td>
      <td>6035</td>
    </tr>
    <tr>
      <th>July</th>
      <td>79206</td>
      <td>0</td>
      <td>12416</td>
      <td>5913</td>
      <td>6236</td>
    </tr>
    <tr>
      <th>August</th>
      <td>79206</td>
      <td>0</td>
      <td>11402</td>
      <td>5913</td>
      <td>6236</td>
    </tr>
    <tr>
      <th>September</th>
      <td>76651</td>
      <td>0</td>
      <td>2062</td>
      <td>5722</td>
      <td>6035</td>
    </tr>
    <tr>
      <th>October</th>
      <td>79206</td>
      <td>38339</td>
      <td>312</td>
      <td>5913</td>
      <td>6236</td>
    </tr>
    <tr>
      <th>November</th>
      <td>76651</td>
      <td>151170</td>
      <td>16</td>
      <td>5722</td>
      <td>6035</td>
    </tr>
    <tr>
      <th>December</th>
      <td>79206</td>
      <td>246425</td>
      <td>0</td>
      <td>5913</td>
      <td>6236</td>
    </tr>
  </tbody>
</table>`;
document.getElementById('monthly_gas_electricity').innerHTML = `
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Electricity (kWh)</th>
      <th>Gas (kWh)</th>
      <th>Gas (m3)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>January</th>
      <td>85443</td>
      <td>230313</td>
      <td>22404</td>
    </tr>
    <tr>
      <th>February</th>
      <td>77186</td>
      <td>206665</td>
      <td>20103</td>
    </tr>
    <tr>
      <th>March</th>
      <td>85664</td>
      <td>122158</td>
      <td>11883</td>
    </tr>
    <tr>
      <th>April</th>
      <td>83597</td>
      <td>46956</td>
      <td>4567</td>
    </tr>
    <tr>
      <th>May</th>
      <td>87595</td>
      <td>5913</td>
      <td>575</td>
    </tr>
    <tr>
      <th>June</th>
      <td>88785</td>
      <td>5722</td>
      <td>556</td>
    </tr>
    <tr>
      <th>July</th>
      <td>97859</td>
      <td>5913</td>
      <td>575</td>
    </tr>
    <tr>
      <th>August</th>
      <td>96846</td>
      <td>5913</td>
      <td>575</td>
    </tr>
    <tr>
      <th>September</th>
      <td>84749</td>
      <td>5722</td>
      <td>556</td>
    </tr>
    <tr>
      <th>October</th>
      <td>85755</td>
      <td>44252</td>
      <td>4304</td>
    </tr>
    <tr>
      <th>November</th>
      <td>82703</td>
      <td>156893</td>
      <td>15262</td>
    </tr>
    <tr>
      <th>December</th>
      <td>85443</td>
      <td>252339</td>
      <td>24546</td>
    </tr>
  </tbody>
</table>`;
