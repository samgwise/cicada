from src.drawing_model import Cicada
import plotly.express as px
import inspect

class Test_Suite:
    """Setup the test, log the outputs, status, completion and all tests"""

    def __init__(self):
        self.test_suite = []

    def add_tests(self, new_tests):
        self.test_suite.append(new_tests)

    def run_tests(self):
        for test_object in self.test_suite:
            t = test_object
            attrs = (getattr(t, name) for name in dir(t))
            methods = filter(inspect.ismethod, attrs)
            for method in methods:
                try:
                    method()
                    print(f"Completed Test from: {type(test_object)}")
                except TypeError:
                    # Can't handle methods with required arguments.
                    pass
        print("Done")

def load_cicada(test_args):
    cicada = Cicada(
        device=test_args.device,
        canvas_w=test_args.canvas_w,
        canvas_h=test_args.canvas_h,
        drawing_area=test_args.drawing_area,
        max_width=test_args.max_width,
    )
    cicada.set_penalizers(
        w_points=test_args.w_points,
        w_colors=test_args.w_colors,
        w_widths=test_args.w_widths,
        w_img=test_args.w_img,
        w_geo=test_args.w_geo,
    )
    cicada.process_text(test_args.prompt)
    cicada.load_svg_shapes(test_args.svg_path)
    cicada.add_random_shapes(test_args.num_paths)
    cicada.initialize_variables()
    cicada.initialize_optimizer()
    return cicada


def run_test(test_args, test_name):
    """Overwwrite args depending on the required setup"""

    plot_x = []
    loss_plot_y = []        
    diversity_plot_x = []
    diversity_plot_y = []

    cicada = load_cicada(test_args)

    #Start
    for t in range(test_args.num_iter):
        cicada.run_epoch()
        plot_x.append(t)
        loss_plot_y.append(float(cicada.losses['global'].item()))

        if t % 10 == 0:
            # UPDATE FOR TIE
            diversity_plot_y.append(float(cicada.losses['global'].item()))

        #Options
        if t == round(test_args.num_iter / 2):
            if test_args.area_kill:
                cicada.mutate_area_kill()

            if test_args.respawn_traces:
                cicada.mutate_respawn_traces()

            if test_args.lr_boost:
                cicada.mutate_lr()

            if test_args.evo_search:
                cicada.evo_search(test_args.num_iter, test_args)    

        utils.printProgressBar(t + 1, args.num_iter, cicada.losses['global'].item())


    fig_loss = px.scatter(x=plot_x, y=loss_plot_y, title=f"Loss score for {test_name}")
    fig_loss.update_layout(xaxis_title="Step", yaxis_title="Loss")
    fig_loss.write_image(f"tests/results/{test_name}_fig_loss.png")

    fig_diversity = px.scatter(x=plot_x, y=diversity_plot_y, title=f"Diversity score for {test_name}")
    fig_diversity.update_layout(xaxis_title="Step", yaxis_title="TIE")
    fig_diversity.write_image(f"tests/results/{test_name}_fig_diversity.png")


