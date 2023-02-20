import torch
import copy
from src.config import args
from src.drawing_model import Cicada

import plotly.express as px

prompt_A = 'A tall red chair.'
NUM_ITER = 300
SVG_PATH = "data/drawing_chair.svg"

class TestEvoSearch:
    def test_prompt_change(self):
        plot_x = []
        plot_y = []

        # Using prompt A #################
        args.prompt = prompt_A
        cicada = Cicada(
            device=args.device,
            canvas_w=args.canvas_w,
            canvas_h=args.canvas_h,
            drawing_area=args.drawing_area,
            max_width=args.max_width,
        )
        cicada.set_penalizers(
            w_points=args.w_points,
            w_colors=args.w_colors,
            w_widths=args.w_widths,
            w_img=args.w_img,
            w_geo=args.w_geo,
        )



        cicada.process_text(args.prompt)
        text_features_A = copy.copy(cicada.text_features)
        cicada.load_svg_shapes(args.svg_path)
        cicada.add_random_shapes(args.num_paths)
        cicada.initialize_variables()
        cicada.initialize_optimizer()

        for t in range(NUM_ITER):
            cicada.run_epoch()
            plot_x.append(t)
            plot_y.append(float(cicada.losses['global'].item()))

        #Mutate

        cicada.mutate_area_kill()
        cicada.mutate_respawn_traces()
        cicada.mutate_lr()
        
        # Running Evo Search        
        cicada.evo_search(t, args)
        
        for t in range(NUM_ITER):
            cicada.run_epoch()
            plot_x.append(NUM_ITER + t)
            plot_y.append(float(cicada.losses['global'].item()))

        fig = px.scatter(x=plot_x, y=plot_y)
        fig.write_image("tests/results/evo_plot_mutate.png")
