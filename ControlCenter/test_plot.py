import numpy as np

# Generate some data
x = np.linspace(0, 2*np.pi, 400)
y = np.sin(x)

# Draw
ax.plot(x, y, label="sin(x)")
ax.set_title("Test Plot")
ax.set_xlabel("x")
ax.set_ylabel("sin(x)")
ax.grid(True)
ax.legend()

# Example annotation to confirm interactivity
ax.annotate("Peak", xy=(np.pi/2, 1), xytext=(2, 1.2),
            arrowprops=dict(arrowstyle="->"))
