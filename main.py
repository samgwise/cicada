from src.drawing_model import Cicada
import torch
import pydiffvg
import datetime
import time
from src import utils
from src.config import args
from pathlib import Path
from src.behaviour import TextBehaviour

from src.logger import Logger

log_path = Path('logs/')
log_path.mkdir(parents=True, exist_ok=True)
log = Logger(log_path)

log.record_parameters(utils.obj2dict(args))

device = torch.device(args.device) if torch.cuda.is_available() else torch.device("cpu")

print(f"Using Device: {device}")
log.event("Init", f"Using Device: {device}", None)

# Build dir if does not exist & make sure using a
# trailing / or not does not matter
save_path = Path("results/").joinpath(args.save_path)
save_path.mkdir(parents=True, exist_ok=True)
save_path = str(save_path) + '/'


log.event("Init", f"save_path: {save_path}", None)

log.record_completion(False)


text_behaviour = TextBehaviour()
text_behaviour.add_behaviour("drawing", "photo")
text_behaviour.add_behaviour("simple", "complex")
text_behaviour.add_behaviour("abstract", "realistic")

t0 = time.time()

prune_places = [
    round(args.num_iter * (k + 1) * 0.8 / args.n_prunes) for k in range(args.n_prunes)
]
p0 = args.prune_ratio


gif_builder = utils.GifBuilder()

for trial in range(args.num_trials):
    args.prune_ratio = p0 / len(prune_places)

    cicada = Cicada(
        device=device,
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

    time_str = (datetime.datetime.today() + datetime.timedelta(hours=11)).strftime(
        "%Y_%m_%d_%H_%M_%S"
    )

    cicada.load_svg_shapes(args.svg_path)
    cicada.add_random_shapes(args.num_paths)
    cicada.initialize_variables()
    cicada.initialize_optimizer()
    with torch.no_grad():
        pydiffvg.imwrite(
            cicada.img0.detach().cpu().squeeze(0).permute(1, 2, 0),
            save_path + time_str + '00.png',
            gamma=1,
        )

    # Run the main optimization loop
    for t in range(args.num_iter):
        if (t + 1) % args.num_iter // 50:
            with torch.no_grad():
                pydiffvg.imwrite(
                    cicada.img,
                    save_path + time_str + '.png',
                    gamma=1,
                )
                if args.build_gif:
                    gif_builder.add(cicada.img)

        cicada.run_epoch()

        if t == args.num_iter // 2 and args.area_kill:
            cicada.mutate_area_kill()

        if t == args.num_iter // 2 and args.respawn_traces:
            cicada.mutate_respawn_traces()

        if t == args.num_iter // 2 and args.lr_boost:
            cicada.mutate_lr()

        # Pruning
        if t in prune_places:
            with torch.no_grad():
                pydiffvg.imwrite(
                    cicada.img,
                    save_path + time_str + f'_preP_{t}.png',
                    gamma=1,
                )
            cicada.prune(args.prune_ratio)
            args.prune_ratio += p0 / len(prune_places)

        if t - 1 in prune_places:
            with torch.no_grad():
                pydiffvg.imwrite(
                    cicada.img,
                    save_path + time_str + f'_postP_{t-1}.png',
                    gamma=1,
                )

        if t == 50 and args.evo_search:
            # cicada.evo_search()
            log.event("Generation", f"Evo Search", t)
            search_results = cicada.run_evolutionary_search(t, args, limit=1, generations=5, seed=10)
            if len(search_results) > 0:
                current_fitness = cicada.evo_fitness(cicada.drawing, t, args)
                if search_results[0]['fitness'] > current_fitness:
                    cicada.drawing = search_results[0]['drawing']
                    log.event("Generation", f"Adopting new drawing from search, continueing gradient descent.", t)
                else:
                    log.event("Generation", f"Search did not find a better drawing, continueing gradient descent.", t)

        log.progress(cicada.losses['global'].item(), t)

        utils.printProgressBar(t + 1, args.num_iter, cicada.losses['global'].item())

    pydiffvg.imwrite(
        cicada.img,
        save_path + time_str + '.png',
        gamma=1,
    )
    utils.save_data(save_path, time_str, args)

    text_behaviour.eval_behaviours(cicada.img, showme=True)

if args.build_gif:
    gif_builder.build_gif(save_path + time_str)

time_sec = round(time.time() - t0)
print(f"Elapsed time: {time_sec//60} min, {time_sec-60*(time_sec//60)} seconds.")


log.record_completion(True)
# Save logs along side the SVGs
report_path = Path(save_path)
log.events_to_file(report_path.joinpath("events.csv"))
log.progress_to_file(report_path.joinpath("progress.csv"))
log.experiment_to_file(report_path)