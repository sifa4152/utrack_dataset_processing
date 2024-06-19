# =============================================================================
# ERA5 Reanalysis Precipitation and Evaporation Analysis
# Simon Felix Fahrländer
# 2023-07-27
# =============================================================================
# IMPORTS
import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import settings

# =============================================================================

# function to calculate total monthly flux
def calc_total_monthly_flux(data, grid_area):
    tot_monthly_data = {}

    for i, t in enumerate(data.month):
        x = np.nansum(data.sel(month=t) * grid_area)
        tot_monthly_data[i+1] = x / 1e12  # Convert to km3

    df = pd.DataFrame(tot_monthly_data.items(), columns=['month','total_flux'])

    return df

# function to calculate total annual flux
def calc_total_annual_flux(data, grid_area):
    tot_annual_data = {}

    years = data.time.dt.year.values.tolist()
    for i, t in enumerate(data.time):
        x = np.nansum(data.sel(time=t) * grid_area)
        tot_annual_data[years[i]] = x / 1e12  # Convert to km3

    df = pd.DataFrame(tot_annual_data.items(), columns=['year','total_flux'])

    return df


# =============================================================================
if __name__ == '__main__':
    """
    ERA5 Reanalysis Water Balance Calculation for UTrack Time Frame (2008-2017)
    Script uses same input as the UTrack database tracking routine --> filepaths are taken from settings.py! 
    """
    # LOAD DATA
    grid_area = xr.open_dataset(settings.GRID_PATH).cell_area

    # ERA5 PRECIPITATION
    precip = xr.open_dataset(settings.PRECIP_PATH).tp.sel(time=slice('2008-01-01',
                                                                    '2017-12-01')
                                                        )
    precip_annual = precip.resample(time='Y').sum(skipna=True)
    precip_mean = precip_annual.mean(dim='time', skipna=True)
    # Convert to multi-year mean
    precip_grouped = precip.groupby('time.month').mean(dim='time')
    precip_grouped = (xr.where(precip_grouped > 0, precip_grouped, 0))


    # ERA5 EVAPORATION
    evap = xr.open_dataset(settings.EVAP_PATH).e.sel(time=slice('2008-01-01',
                                                                '2017-12-01')
                                                    )
    evap_annual = evap.resample(time='Y').sum(skipna=True)
    evap_mean = evap_annual.mean(dim='time', skipna=True)
    # Convert to multi-year mean
    evap_grouped = evap.groupby('time.month').mean(dim='time')
    evap_grouped = (xr.where(evap_grouped > 0, evap_grouped, 0))


    # =============================================================================
    # MONTHLY FLUXES

    P_flux_monthly = calc_total_monthly_flux(precip_grouped, grid_area)
    E_flux_monthly = calc_total_monthly_flux(evap_grouped, grid_area)

    # PLOT MONTHLY FLUXES
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(P_flux_monthly.month,
            P_flux_monthly.total_flux,
            label='Precipitation',
            c='darkblue'
            )
    ax.plot(E_flux_monthly.month,
            E_flux_monthly.total_flux,
            label='Evaporation',
            c='darkred'
            )

    # Set the tick locations and labels for the x-axis
    ax.set_xticks(P_flux_monthly.month)
    ax.set_xticklabels(P_flux_monthly.month, fontsize=14)

    # Add y-axis title and figure title
    ax.set_ylabel('Monthly Flux (km$^3$)', fontsize=14)
    ax.set_xlabel('Month', fontsize=14)
    ax.set_title('ERA5 Monthly Global Precipitation and Evaporation Fluxes (2008-2017)',
                fontsize=16
                )

    # Set the limits of the x-axis to the range of the data
    ax.set_xlim(P_flux_monthly.month.iloc[0] - 0.1,
                P_flux_monthly.month.iloc[-1] + 0.1
                )

    ax.legend(loc='upper left', fontsize=13, frameon=False)
    fig.tight_layout()
    plt.show()


    # =============================================================================
    # ANNUAL FLUXES

    P_flux = calc_total_annual_flux(precip_annual, grid_area)
    E_flux = calc_total_annual_flux(evap_annual, grid_area)


    # PLOT ANNUAL FLUXES
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(P_flux.year, P_flux.total_flux, label='Precipitation', c='darkblue')
    ax.plot(E_flux.year, E_flux.total_flux, label='Evaporation', c='darkred')

    # Calculate the mean between the two lines
    mean = (P_flux.total_flux + E_flux.total_flux) / 2

    # Plot the mean as a new line
    ax.plot(P_flux.year, mean, label='Mean', c='k', linestyle='--')

    # Calculate the difference between the two lines
    diff = P_flux.total_flux - E_flux.total_flux

    # Add arrows to indicate the difference between the two lines
    for i in range(len(P_flux.year)):
        x = P_flux.year[i]
        y1 = P_flux.total_flux[i]
        y2 = E_flux.total_flux[i]
        d = diff[i]
        if d > 0:
            ax.annotate('',
                        xy=(x, y1),
                        xytext=(x, y2),
                        arrowprops=dict(arrowstyle='<->', color='darkgreen')
                        )
        elif d < 0:
            ax.annotate('',
                        xy=(x, y2),
                        xytext=(x, y1),
                        arrowprops=dict(arrowstyle='<->', color='darkgreen')
                        )

    # Set the tick locations and labels for the x-axis
    ax.set_xticks(P_flux.year)
    ax.set_xticklabels(P_flux.year, rotation=45, fontsize=13)

    # Set the tick locations and labels for the y-axis
    yticks = ax.get_yticks()
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y:.0f}' for y in yticks], fontsize=13)

    # Format y-axis tick labels to not show any decimal places
    from matplotlib.ticker import ScalarFormatter
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    # Add y-axis title and figure title
    ax.set_ylabel('Total Flux (km$^3$)', fontsize=14)
    ax.set_title('ERA5 Total Global Precipitation and Evaporation Fluxes (2008-2017)',
                fontsize=16
                )

    # Set the limits of the x-axis to the range of the data
    ax.set_xlim(P_flux.year.iloc[0] - 0.1, P_flux.year.iloc[-1] + 0.1)

    ax.legend(loc='upper left', fontsize=13, frameon=False)
    fig.tight_layout()
    plt.show()

    # =============================================================================
    # Calculate ERA5 correction factors (alpha = mean / flux)
    alpha_P = mean / P_flux.total_flux
    alpha_ET = mean / E_flux.total_flux

    tot_alpha_P = alpha_P.mean()
    tot_alpha_ET = alpha_ET.mean()

    print(f'Total alpha_P: {tot_alpha_P:.2f}')
    print(f'Total alpha_ET: {tot_alpha_ET:.2f}')
    print("Don't forget to adjust factors in settings.py of UTrack database tracking routine!")


    # Gridcell monthly correction factors (problem: division by zero in Arctic, Antarctic and desert regions)
    # mean_grouped = (precip_grouped  + evap_grouped) / 2
    # alpha_P_grouped = mean_grouped / precip_grouped
    # alpha_ET_grouped = mean_grouped / evap_grouped

    # P_monthly_tot_mean = [np.nanmean(precip_grouped[i,:,:]) for i in range(0, 12)]
    # E_monthly_tot_mean = [np.nanmean(evap_grouped[i,:,:]) for i in range(0, 12)]
    # monthly_tot_mean = [(P_monthly_tot_mean[i] + E_monthly_tot_mean[i]) / 2 for i in range(0, 12)]

    # alpha_P_monthly = [monthly_tot_mean[i] / P_monthly_tot_mean[i] for i in range(0, 12)]
    # alpha_E_monthly = [monthly_tot_mean[i] / E_monthly_tot_mean[i] for i in range(0, 12)]

