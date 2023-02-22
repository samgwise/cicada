import os
import pickle
import torch
import pandas as pd
from mapelites_config import args
from drawing_model import Cicada
from behaviour import TextBehaviour

#
# Preliminaries
#
device = "cuda:0" if torch.cuda.is_available() else "cpu"

k = 0
while os.path.exists(f"{args.save_path}_{k}"):
    k += 1
save_path = f"{args.save_path}_{k}"
os.makedirs(save_path)
delattr(args, "save_path")

text_behaviour = TextBehaviour()
behaviour_dims =[x.split("|") for x in args.behaviour_dims.split("||")]
for bd in behaviour_dims:
    text_behaviour.add_behaviour(bd[0], bd[1])
df = pd.DataFrame(columns=["in_population", "orig_iter", "fitness"]+[beh["name"] for beh in text_behaviour.behaviours])

#
# Aux
#
def run_cicada(cicada, args):
    cicada.set_penalizers(
        w_points=args.w_points,
        w_colors=args.w_colors,
        w_widths=args.w_widths,
        w_geo=args.w_geo,
    )
    cicada.process_text(args.prompt)
    cicada.load_svg_shapes(args.svg_path)
    cicada.add_random_shapes(args.num_paths)
    cicada.initialize_variables()
    cicada.initialize_optimizer()
    losses = []
    behs = []
    for t in range(args.num_iter):
        cicada.run_epoch()
        if t > args.num_iter-11:
            with torch.no_grad():
                losses.append(cicada.losses["global"].detach())
                behs.append(text_behaviour.eval_behaviours(cicada.img))
    
    loss = torch.mean(torch.cat(losses)).item()
    behs = torch.mean(torch.cat([b.unsqueeze(0) for b in behs]), dim=0)
    fitness = 1-loss
    behs = [b.item() for b in behs]
    return fitness, behs, cicada.drawing

def id_check(id, grids):
    for grid_name in grids:
        for individual in grids[grid_name]["individuals"]:
            if individual["id"] == id:
                return True
    return False

#
# MAPELITES
#

# Generate population
# for k in range(args.population_size):
#     cicada = Cicada(
#         device=device,
#         drawing_area=args.drawing_area,
#         max_width=args.max_width,
#     )
    
#     fitness, behs, drawing = run_cicada(cicada, args)
#     df.loc[drawing.id] = [False, 0, fitness] + behs
#     with open(f"{save_path}/{drawing.id}.pkl", "wb") as f:
#         pickle.dump(drawing, f)
#     df.to_csv(f"{save_path}/df.csv", index_label="id")

df = pd.read_csv("results/mapelites/chair_10/df.csv", index_col="id")

# Build grids
grids = {}
for beh in text_behaviour.behaviours:
    x = list(df[beh['name']])
    mx = min(x)
    Mx = max(x)
    grid_min = mx - 0.1*(Mx-mx)
    grid_max = Mx + 0.1*(Mx-mx)
    grid = [grid_min + k*(grid_max-grid_min)/(args.grid_size-2) for k in range(args.grid_size-1)]
    grids[beh['name']] = {
        "values": grid,
        "individuals": [{"id": None, "fitness":-1e5} for x in range(args.grid_size)],
    }

# Fill grids
for id in df.index:
    x = df.loc[id]
    for grid_name in grids:
        grid_idx = 0
        for value in grids[grid_name]["values"]:     
            if x[grid_name] < value:
                break
            else:
                grid_idx += 1
        
        if grids[grid_name]["individuals"][grid_idx]["fitness"] < x["fitness"]:                
            grids[grid_name]["individuals"][grid_idx]["id"] = id
            grids[grid_name]["individuals"][grid_idx]["fitness"] = x["fitness"]

print("Initial Population")
for grid_name in grids:
    print(grid_name)
    print(grids[grid_name]["individuals"])
print('')

for id in df.index:
    x = df.loc[id]
    x["in_population"] = id_check(id, grids)
    df.loc[id] = x

print(df)