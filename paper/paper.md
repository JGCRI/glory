---
title: 'GLORY: a Python package for global reservoir water yield and cost estimation'
tags:
  - Python
  - global reservoir water yield
  - reservoir cost
authors:
  - name: Mengqi Zhao
    orcid: 0000-0001-5385-2758
    affiliation: 1
  - name: Thomas B. Wild
    orcid: 0000-0002-6045-7729
    affiliation: 2
  - name: Chris R. Vernon
    orcid: 0000-0002-3406-6214
    affiliation: 1
affiliations:
 - name: Pacific Northwest National Laboratory, Richland, WA, USA
   index: 1
 - name: Joint Global Change Research Institute, College Park, MD, USA
   index: 2
date: June 2024
bibliography: paper.bib
---

# Summary
The `GLORY` (GLObal Reservoir Yield) model is an open-source Python package designed to estimate the economic costs associated with supplying 
increasing levels of water yield from reservoir storage across the world's large river basins (\autoref{fig:workflow}). For each river basin, the model first uses linear
programming to optimize a reservoir release strategy designed to maximize the annual basin-wide volumetric yield of water that can be achieved
for increasing levels of reservoir storage capacity, subject to geophysical constraints. For example, the model conducts a monthly time-step reservoir water 
balance that accounts for the sub-annual timing of streamflow (i.e., reservoir inflows), surface water evaporation, reservoir release, environmental flows, return flows, 
and spills. Other constraints include the sub-annual timing of water demands, and the suitability of riverine corridors for reservoir construction. 
The result of the optimization is a single capacity-yield curve for each of 235 global river basins that describes the annual volumetric water yield that can be obtained through incremental 
increases in a basin's total reservoir storage capacity. The model's focus on maximizing yield makes it more amenable to the study of irrigation and water supply reservoir potential. 
Next, the model converts each capacity-yield curve into a supply cost curve by converting each level of reservoir storage capacity volume on the curve into a levelized cost of water supply, taking into account physiographically specific reservoir construction costs and other specifications (e.g., reservoir size).
On their own, capacity-yield and cost curves are useful for various analyses of water resources systems [@Liu_2018], 
including continental to global scale economic analyses of reservoir storage expansion. Additionally, `GLORY`'s cost curves are designed to be used in hydro-economic or 
coupled human-Earth systems assessments that require as input an economic valuation of the cost of water supply to explore multi-sector dynamic [@Reed_2022] interactions. 
For example, `GLORY` can be used to produce surface water cost curve inputs [@Zhao_2024] for the Global Change Analysis Model (`GCAM`), 
which can in turn be used to explore the future co-evolution of energy, water, and land systems under global change [@Calvin_2019].

![The GLORY model workflow showing the input data requirements and the steps of modeling capacity-yield relationships and supply curves. \label{fig:workflow}](workflow.png)


# Statement of Need
Extensive research literature is devoted to advancing methods for modeling the physical (as opposed to economic) characteristics of reservoirs, from models that operate at the scale of individual reservoirs 
or systems of reservoirs [@Wild_2021] to global hydrology models [@Abeshu_2023]. These efforts have focused primarily
on modeling the operations of existing reservoir fleets to meet various objectives. There is growing interest in understanding the future role reservoirs could play in meeting water demands [@Sen_2021; @Schmitt_2022], 
but there is a gap in economics-based modeling methods and software to support analyses of future expansion of dam and reservoir infrastructure [@Vanderkelen_2021; @Zhao_2024]. 
Hydro-economic and global multi-sector dynamic models (e.g., `GCAM`) are designed to explore (at global scale) future multi-sector water demands under global change (e.g., socioeconomic and climate change), and the competition between surface water reservoirs and other 
sources of water supply (e.g., groundwater) to meet those demands [@Rising_2020]. However, these global integrated multi-sector models often require regionally differentiated cost curves that describe the cost to supply increasing quantities of surface water [@Harou_2009; @Strzepek_2013; @Kim_2016; @Graham_2018].
`GLORY` fills a gap by providing these cost curves. `GLORY` was recently coupled with `GCAM` to create a more dynamic representation of water storage than the model's existing representation of surface water supply cost [@Kim_2016].
Finally, the model produces capacity-yield curves that are also useful continental-to-global scale analyses of reservoir storage and yield potential [@Liu_2018]. 

# State of the Field
The field of hydro-economic modeling has seen limited application at the global scale. One notable exception is the Global Hydro-economic Model (`ECHO`) [@Kahil_2018], which aims to inform cost-effective and sustainable water policies by minimizing total water management costs across the water, land, and energy sectors. However, `ECHO` does not offer comparable functionality in terms of the hydro-economic aspects of reservoirs across their full exploitable potential on a global scale. In contrast, the `GLORY` model provides unique functionalities that streamline workflows by integrating information on climate, hydrology, water demand, reservoir exploitable potential, and physiography to estimate the water availability and prices of water supply from reservoirs. These capabilities enable `GLORY` to complement models like `ECHO` or other multisector dynamics models like `GCAM`, enhancing their hydro-economic analyses within an integrated context.

# Design and Functionality
The `GLORY` model is designed to integrate complex processes of estimating reservoir water yield and cost into a pipeline. `GLORY` utilizes human-readable YAML file for easy model configuration. It can be applied to analyze either global basins or a subset of basins and periods of interest. Instead of relying on the default basin delineation, users can also switch to customized geographical boundaries, given the relevant data is available. The modular design of `GLORY` offers users the flexibility to use individual module or the entire model, depending on their interest in the water management or the economics of water supply. 

Here we briefly demonstrate how to use `GLORY` to achieve different outcomes. One can effortlessly apply the `glory.lp_model()` function to execute a linear programing model that determines the optimized water yield for a given reservoir storage capacity. To generate a capacity-yield curve and a supply curve with discrete points for a single basin (e.g., Figure 2), users can easily instantiate the `glory.SupplyCurve()` object by providing the configuration object. The `glory.SupplyCurve()` will then undertake the process of identifying reservoir storage capacity expansion pathways and calculating the optimized water yield at each storage capacity point. To apply `GLORY` to multiple basins, simply indicate the basin IDs in the configuration file and run the `GLORY` model using `glory.run_model()`. \autoref{fig:curve} shows an example output of capacity-yield curve and supply curve for Pacific Northwest basin in the United States. The water supply curve has been widely used in `GCAM` to inform the water management cost to supply water in the economic market. The detailed documentation on how to use `glory` can be accessed at [glory documentation](https://jgcri.github.io/glory/index.html).

![The example diagnostic output from `GLORY` model for the capacity-yield curve (top) and water supply curve (bottom) for the Pacific Northwest basin. \label{fig:curve}](curve_pnw.png)

# Acknowledgements
This research was supported by the U.S. Department of Energy, Office of Science, as part of research in MultiSector Dynamics, Earth and Environmental System Modeling Program.

# References
