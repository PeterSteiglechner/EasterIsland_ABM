import xarray as xr
import numpy as np
import pandas as pd


def store_agg_values(model):
    model.n_agents_arr.append(len(model.schedule))
    model.resource_motivated_moves_arr.append(model.resource_motivated_moves)
    model.excess_deaths_arr.append(model.excess_deaths)
    model.excess_births_arr.append(model.excess_births)
    satisfactions = np.array([ag.satisfaction for ag in model.schedule])
    model.mean_satisfactions_arr.append(np.mean(satisfactions) if len(model.schedule) > 0 else 0)
    model.std_satisfactions_arr.append(np.std(satisfactions) if len(model.schedule) > 0 else 0)
    tree_fills = np.array([ag.tree_fill for ag in model.schedule])
    cult_fills = np.array([ag.cult_fill for ag in model.schedule])
    model.n_tree_unfilled_arr.append(np.sum(tree_fills < 1) if len(model.schedule) > 0 else 0)
    model.n_cult_unfilled_arr.append(np.sum(cult_fills < 1) if len(model.schedule) > 0 else 0)
    model.mean_tree_fill_arr.append(np.mean(tree_fills) if len(model.schedule) > 0 else 0)
    model.mean_cult_fill_arr.append(np.mean(cult_fills) if len(model.schedule) > 0 else 0)
    fractions_poor_vs_well = [np.sum(ag.arability_cultivated_gardens == model.arability_poor) /
                              max(len(ag.arability_cultivated_gardens), 1) for ag in model.schedule]
    model.fractions_poor_vs_well_arr.append(np.mean(fractions_poor_vs_well) if len(model.schedule) > 0 else 0)

    model.excess_deaths = 0
    model.excess_births = 0
    model.resource_motivated_moves = 0

    return


def store_agents_values(model, time):
    index = pd.MultiIndex.from_product([[time], [int(ag.index) for ag in model.schedule]], names=["time", "id"])
    agents_stats = [np.array([time, int(ag.index), ag.x, ag.y, ag.p, len(ag.arability_cultivated_gardens), ag.t_pref],
                             dtype=np.float) for ag in model.schedule]
    if len(model.schedule) == 0:
        agents_stats = [np.array([np.nan for _ in model.agents_stats_columns])]
    agents_stats_current = pd.DataFrame(agents_stats, columns=model.agents_stats_columns, index=index)
    if time == model.time_arrival:
        model.agents_stats = agents_stats_current
    else:
        model.agents_stats = model.agents_stats.append(agents_stats_current)
    return


def store_const_map(model):
    coast = np.zeros_like(model.map.triobject.mask).astype(bool)
    coast[model.map.coast_triangle_inds] = True

    const_map_values = \
        xr.Dataset(
            {
                "triangles": (("inds_all", "triangle_corners"), model.map.triobject.triangles),
                "mask": ("inds_all", model.map.triobject.mask),
                "y": ("ind_points", model.map.triobject.y),
                "x": ("inds_points", model.map.triobject.x),
                "midpoints": (("inds_all", "space"), model.map.midpoints),
                "coast": ("inds_map", coast[model.map.inds_map]),
                "sl": ("inds_map", model.map.sl_map),
                "el": ("inds_map", model.map.el_map),
                "dist_to_water": ("inds_map", model.map.dist_water_map),
                "dist_to_coast": ("inds_map", model.map.dist_to_coast_map),
                "arability": ("inds_map", model.map.arability_c),
                "trees_cap": ("inds_map", model.map.trees_cap)
            },
            coords={
                "space": ["x", "y"],
                "triangle_corners": [0, 1, 2],
                "inds_map": model.map.inds_map,
                "inds_all": np.arange(len(model.map.triobject.mask)),
                "inds_points": np.arange(len(model.map.triobject.x))
            },
        )
    const_map_values.attrs["n_all"] = len(model.map.triobject.mask)
    const_map_values.attrs["anakena_ind_map"] = model.map.anakena_ind_map
    const_map_values.attrs["area_map_m2"] = model.map.area_map_m2
    const_map_values.attrs["triangle_area_m2"] = model.map.triangle_area_m2
    const_map_values.attrs["n_gardens_percell"] = model.map.n_gardens_percell
    const_map_values.to_netcdf(path=model.folder + "const_map_values.ncdf")
    return


def store_dynamic_map(model, time):
    """ Store current data over time """
    n = np.where(time == model.time_range)[0][0]

    model.trees[n, :] = model.map.trees_map
    model.gardens[n, :] = model.map.cultivated_gardens
    model.population[n, :] = model.map.pop_cell
    model.clearance[n, :] = model.map.tree_clearance
    model.lakes[n, model.map.water_cells_map] = True
    return


def save_all(model):
    # constant map
    store_const_map(model)

    # store attributes of single agents
    model.agents_stats.to_csv(path_or_buf=model.folder+"ags_stats.csv")

    # global aggregate:
    save_agg_values = xr.Dataset(
        {
            "n_agents": (["time"], model.n_agents_arr),
            "resource_motivated_moves": (["time"], model.resource_motivated_moves_arr),
            "excess_deaths": (["time"], model.excess_deaths_arr),
            "excess_births": (["time"], model.excess_births_arr),
            "mean_satisfactions": (["time"], model.mean_satisfactions_arr),
            "std_satisfactions": (["time"], model.std_satisfactions_arr),
            "n_tree_unfilled": (["time"], model.n_tree_unfilled_arr),
            "n_cult_unfilled": (["time"], model.n_cult_unfilled_arr),
            "mean_tree_fill": (["time"], model.mean_tree_fill_arr),
            "mean_cult_fill": (["time"], model.mean_cult_fill_arr),
            "fractions_poor_vs_well": (["time"], model.fractions_poor_vs_well_arr),
        },
        {
            "time": model.time_range,
        }
    )
    save_agg_values.to_netcdf(path=model.folder + "aggregate_values.ncdf")

    # dynamic environment
    dynamic_env = xr.Dataset(
        {
            "trees": (["time", "cell_ind"], model.trees),
            "gardens": (["time", "cell_ind"], model.gardens),
            "population": (["time", "cell_ind"], model.population),
            "clearance": (["time", "cell_ind"], model.clearance),
            "lakes": (["time", "cell_ind"], model.lakes),
        },
        {
            "time": model.time_range,
            "cell_ind": model.map.inds_map
        }
    )
    dynamic_env.to_netcdf(path=model.folder + "dynamic_env.ncdf")
