# Understanding Pump Curves

A pump curve (also called a performance curve) is a chart every pump manufacturer publishes for each of their pump models. It shows how that pump actually behaves across its full operating range — not just at one design point — so you can confirm it will do what you need before it's ordered, installed, and running on-site.

## What's plotted on a pump curve

Every pump curve plots several relationships against **flow rate** (typically L/s or m³/hr) along the bottom axis:

- **Head curve** — how much pressure (in metres, or sometimes kPa) the pump can produce at a given flow. This always slopes downward: the more flow a pump delivers, the less head it can generate at the same time.
- **Efficiency curve(s)** — how much of the input power is actually converted into useful hydraulic work, shown as a percentage. Efficiency rises to a peak — the **Best Efficiency Point (BEP)** — then falls off again on either side.
- **Power curve** — the motor power (kW) the pump draws at each flow rate, so you can confirm the motor is sized correctly across the operating range.
- **NPSH Required (NPSHr)** — the minimum suction-side pressure the pump needs at its inlet to avoid cavitation. This rises as flow increases, and needs to stay below whatever suction pressure your actual system can supply (NPSH *Available*).

## Why this matters for pump selection

Picking a pump purely off its nameplate or catalogue duty point — without checking the full curve against your system's actual conditions — is one of the most common (and expensive) mistakes in HVAC and hydraulic design. Checking the curve properly lets you:

- Confirm the pump can actually reach your required duty point (design flow and head) once installed
- Avoid running the pump well away from its BEP, which wastes energy over the system's lifetime
- Keep NPSH available above NPSH required, avoiding cavitation and premature wear
- Stay within the manufacturer's allowable operating range, avoiding vibration, seal damage, and bearing wear from running too far to either side of the curve

## Further viewing

Masterflow Solutions has a short video explainer covering how to read a pump performance curve: [Pump Performance Curve: What It Is & How to Read It](https://www.youtube.com/watch?v=46YMjrbihMg) (Masterflow Solutions, YouTube).

## Try it yourself — interactive diagram

Use the toggles below to show or hide each curve individually, and hover over any line for an explanation of what it represents.

<iframe src="http://localhost:8050/apps/pump-curve-diagram" width="100%" height="750" style="border:0"></iframe>