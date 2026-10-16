# Selecting a Pump Curve

This page walks through how to find the correct performance curve for a specific pump already installed or specified on a project. You'll typically be starting from two things: the **pump nameplate** and the **motor nameplate**.

## Step 1 — Read the pump nameplate

Most pump nameplates include some or all of the following. Note these all down before searching for the curve — the more of these you have, the easier it is to confirm you've found the *exact* right curve, not just a similar model.

| Field | What it tells you |
|---|---|
| Manufacturer & model/type | Which brand's selection tool or catalogue to search |
| Serial number | Uniquely identifies this specific unit — useful if the model number alone brings up several variants |
| Duty point (flow @ head) | The flow and head this pump was originally selected to deliver |
| Speed (RPM) | Needed to identify the right curve, since the same casing can be built for multiple speeds |
| Impeller diameter | Many pump curves show several lines for different impeller trims within the same casing — you need this to pick the right line |
| Max operating pressure | Confirms the pump is suitable for your system's working pressure |
| Casing material | Relevant for compatibility with the fluid being pumped |

## Step 2 — Read the motor nameplate

The motor nameplate confirms the pump's duty point is achievable without overloading the motor. Key fields:

| Field | What it tells you |
|---|---|
| Rated power (kW/HP) | Compare against the power curve at your actual duty point — the motor must have enough headroom across the expected operating range, not just at the nameplate duty point |
| Voltage & phase | Confirms electrical compatibility with the site supply |
| Full load current (FLA) | Used to check against actual measured current during commissioning |
| Speed / poles | Should match the pump's rated speed |
| Frame size | Relevant if the motor ever needs replacing |
| IP rating | Confirms the motor is suitable for its installation environment (e.g. outdoor, wet plant room) |
| Insulation class & service factor | Relevant for motor longevity and overload tolerance |

## Step 3 — Locate the manufacturer's performance curve

Once you have the model, speed, and impeller diameter from Step 1, use the relevant manufacturer's tool below to pull the actual curve. Each link opens in a new tab.

| Brand | Selection Tool | Notes | Contact |
|---|---|---|---|
| Masterflow | <a href="https://masterflow.pump-flo.com/app/storefront.aspx?ReturnUrl=%2fapp%2fstorefront.aspx%3fsid%3dmasterflow&sid=masterflow" target="_blank">Pump-Flo Selector</a> | Requires a Masterflow account login. | sales@masterflow.net.au |
| Grundfos | <a href="https://product-selection.grundfos.com/" target="_blank">Grundfos Product Center</a> | Replaced the older "WebCAPS" tool — old bookmarked WebCAPS links redirect here automatically. | contact-au@grundfos.com |
| KSB | <a href="https://www.ksb.com/en-au" target="_blank">KSB Australia</a> | Also worth checking with local resellers such as Superpumps, who may hold curves for the KSB pumps they distribute even if KSB's own site doesn't turn up an exact match. | enquiries@ksb.com.au |
| Wilo | <a href="https://wilo.com/au/en/Catalogue/en/products" target="_blank">Wilo Product Catalogue</a> | — | sales.au@wilo.com |

**A general tip:** an AI assistant (like Claude or ChatGPT) can also be genuinely useful for tracking down a pump curve — for example, giving it the model number and nameplate details and asking it to identify the manufacturer, likely curve family, or where that data is typically published. It won't replace the manufacturer's own tool, but it's often a fast way to narrow down where to look.