import matplotlib.pyplot as plt


class Plot:
    def plot(self, x_values, y_values, subtitle):
        fig, ax = plt.subplots()
        ax.plot(x_values, y_values)
        fig.suptitle(subtitle)
