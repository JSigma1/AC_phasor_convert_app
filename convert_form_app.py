# streamlit_app.py
import math
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

#---------- Helpers ----------
def to_rect(mag: float, ang: float, degrees: bool = True):
    """Polar/Exponential (mag∠ang) -> Rectangular (x + jy)."""
    theta = math.radians(ang) if degrees else ang
    x = mag * math.cos(theta)
    y = mag * math.sin(theta)
    return x, y

def to_polar(x: float, y: float, degrees: bool = True):
    """Rectangular (x + jy) -> Polar/Exponential (mag∠ang)."""
    mag = math.hypot(x, y)
    ang = math.atan2(y, x)
    return (mag, math.degrees(ang)) if degrees else (mag, ang)

def complex_latex(x: float, y: float, p: int):
    """Return LaTeX for x + j y with proper sign."""
    sign = "+" if y >= 0 else "-"
    return rf"\displaystyle {x:.{p}f}\ {sign}\ j{abs(y):.{p}f}"

def polar_latex(mag: float, ang: float, p: int, degrees: bool = True):
    """Return LaTeX for mag ∠ ang and mag e^{j ang}."""
    if degrees:
        angle_tex = rf"{ang:.{p}f}^\circ"
    else:
        angle_tex = rf"{ang:.{p}f}"
    rect_arrow = rf"\displaystyle {mag:.{p}f}\,\angle\,{angle_tex}"
    expo = rf"\displaystyle {mag:.{p}f}\,e^{{j\,{angle_tex}}}"
    return rect_arrow, expo

def wrap_angle(ang: float, degrees: bool = True):
    """Wrap angle to (-180, 180] degrees or (-π, π] radians for nice display."""
    if degrees:
        a = ((ang + 180) % 360) - 180
    else:
        a = ((ang + math.pi) % (2 * math.pi)) - math.pi
    return a

#---------- Page config ----------
st.set_page_config(page_title="AC Phasor Converter", page_icon="⚡", layout="centered")

st.title("⚡ AC Phasor Converter")
st.caption("Convert between rectangular (x + j y) and polar/exponential (M∠θ / M e^{jθ}).")

#---------- Sidebar controls ----------
st.sidebar.header("Settings")
mode = st.sidebar.radio("Conversion mode", ["Polar → Rectangular", "Rectangular → Polar"])
angle_unit = st.sidebar.radio("Angle unit", ["Degrees", "Radians"])
deg = angle_unit == "Degrees"
precision = st.sidebar.slider("Display precision (decimal places)", 0, 6, 3)
show_plot = st.sidebar.checkbox("Show phasor plot", value=True)
wrap = st.sidebar.checkbox("Wrap angle to ±180° (or ±π)", value=True)

#---------- Inputs & Compute ----------
if mode == "Polar → Rectangular":
    st.subheader("Input (Polar / Exponential)")
    col1, col2 = st.columns(2)
    with col1:
        mag = st.text_input("Magnitude (M ≥ 0)",value="5.0")
        try :
            mag = float(mag)
            if mag <= 0 :
                st.warning("Value error magnitude can be only positive")
        except ValueError :
            mag = 0.0

    with col2:
        default_angle = "30.0" if deg else f"{math.pi/6}"
        ang = st.text_input(f"Angle θ ({'°' if deg else 'rad'})", value=float(default_angle))
        try :
            ang = float(ang)
        except ValueError:
            ang = 0.0

    x, y = to_rect(mag, ang, degrees=deg)
    z = complex(x, y)

    st.subheader("Result (Rectangular)")
    st.latex(complex_latex(x, y, precision))

    st.subheader("Also as Phasor")
    disp_ang = wrap_angle(ang, degrees=deg) if wrap else ang
    phasor_arrow, phasor_expo = polar_latex(mag, disp_ang, precision, degrees=deg)
    st.latex(phasor_arrow)
    st.latex(phasor_expo)

else:
    st.subheader("Input (Rectangular)")
    col1, col2 = st.columns(2)
    with col1:
        x = st.text_input("Real part x", value="4.33")
        try :
            x = float(x)
        except ValueError :
            x = 0.0
    with col2:
        y = st.text_input("Imag part y (coefficient of j)", value="2.5")
        try :
            y = float(y)
        except ValueError :
            y = 0.0

    mag, ang = to_polar(x, y, degrees=deg)
    if wrap:
        ang = wrap_angle(ang, degrees=deg)
    z = complex(x, y)

    st.subheader("Result (Polar / Exponential)")
    phasor_arrow, phasor_expo = polar_latex(mag, ang, precision, degrees=deg)
    st.latex(phasor_arrow)
    st.latex(phasor_expo)

    st.subheader("Also as Rectangular")
    st.latex(complex_latex(x, y, precision))

#---------- Extra info ----------
with st.expander("Show numeric values"):
    st.write(
        {
            "real (x)": round(z.real, precision + 2),
            "imag (y)": round(z.imag, precision + 2),
            "magnitude (|z|)": round(abs(z), precision + 2),
            "angle (θ, " + ("deg" if deg else "rad") + ")": round(
                math.degrees(np.angle(z)) if deg else float(np.angle(z)), precision + 2
            ),
        }
    )

#---------- Phasor plot ----------
if show_plot:
    st.subheader("Phasor Plot")
    fig, ax = plt.subplots()

    ax.axhline(0, linewidth=1)
    ax.axvline(0, linewidth=1)

    ax.quiver(0, 0, z.real, z.imag, angles='xy', scale_units='xy', scale=1)

    max_abs = max(1.0, abs(z.real), abs(z.imag))
    ax.set_xlim(-1.2 * max_abs, 1.2 * max_abs)
    ax.set_ylim(-1.2 * max_abs, 1.2 * max_abs)
    ax.set_aspect('equal', 'box')
    ax.set_xlabel("Real")
    ax.set_ylabel("Imag (j)")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)


    mag_plot = abs(z)
    ang_plot = math.degrees(np.angle(z)) if deg else float(np.angle(z))
    ang_disp = wrap_angle(ang_plot, degrees=deg) if wrap else ang_plot

    angle_unit_tex = r"^\circ" if deg else ""
    label_tex = rf"$|z|={mag_plot:.{precision}f},\ \theta={ang_disp:.{precision}f}{angle_unit_tex}$"

    ax.annotate(
        label_tex,
        xy=(z.real, z.imag),
        xytext=(10, 10),              
        textcoords="offset points",
        ha="left", va="bottom",
        arrowprops=dict(arrowstyle="->", lw=1, shrinkA=0, shrinkB=0)
    )

    st.pyplot(fig)


#---------- Footer ----------
st.markdown("---")
st.caption("Made by js")