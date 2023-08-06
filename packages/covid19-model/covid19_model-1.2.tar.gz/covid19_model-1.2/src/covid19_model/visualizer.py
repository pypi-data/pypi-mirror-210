import matplotlib.pyplot as plt


def visualize(solution, n, tspan, args, labels, save=False):
    t_0, t_max = tspan[0], tspan[-1]
    beta, gamma = args[0], args[1]

    fig = plt.figure(figsize=(12, 4), constrained_layout=True)
    spec = fig.add_gridspec(2, 2, width_ratios=[2, 1], height_ratios=[3, 2])

    ax1 = fig.add_subplot(spec[0, 0])
    ax2 = fig.add_subplot(spec[1, 0])
    ax3 = fig.add_subplot(spec[:, 1])

    c = 0
    for x in solution:
        ax1.plot(tspan, x, '-', label=labels[c])
        c += 1
    ax1.legend(loc='center right')
    ax1.set_xlim(t_0, t_max)
    ax1.set_ylim(0, 1)

    reprod = beta/gamma*solution[0]
    ax2.plot(tspan, reprod, 'k', label=r"$R_e$")
    ax2.plot([t_0, t_max], [1, 1], 'k:')
    ax2.legend()
    ax2.set_xlim(t_0, t_max)

    ax3.plot(solution[0], solution[1], 'k')
    ax3.set_xlim(0, None)
    ax3.set_ylim(0, None)

    if save:
        loc = f"figures/{save}.pdf"
        plt.savefig(loc)
        return fig, loc
    else:
        return fig, None
