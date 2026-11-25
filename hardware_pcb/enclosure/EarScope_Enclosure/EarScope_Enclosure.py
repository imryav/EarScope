# EarScope enclosure generator for Autodesk Fusion 360 (Python API).
# Board data taken from hardware_pcb/EarScope_XIAO_RA4M1/EarScope_XIAO_RA4M1.kicad_pcb
#   Outline 48 x 25 mm, no mounting holes
#   A1 XIAO RA4M1: USB-C overhangs left edge (x=0) by 2 mm, centre y=10
#   J1 PJ-320A AUX: opening on right edge (x=48), centre y=8.8
#   LED1 (18.95, 23.6), LED2 (11.33, 23.6)
# KiCad Y points down; here Fusion Y = PCB_H - KiCad Y.
# All values in mm. Edit, then re-run. Heights marked VERIFY should be
# measured on the real parts with calipers.

import adsk.core, adsk.fusion, traceback

# ---------------- parameters (mm) ----------------
PCB_W, PCB_H, PCB_T = 48.0, 25.0, 1.6
CLR       = 0.4    # gap PCB edge <-> inner wall
WALL      = 2.0
FLOOR     = 2.0
STANDOFF  = 2.0    # floor top -> PCB bottom
PARTS_H   = 6.0    # tallest part above PCB top (J1 ~5 mm)  VERIFY
TOP_GAP   = 0.5
LID_T     = 1.6
LIP_H     = 2.0    # lid lip depth into base
LIP_W     = 1.2    # lid lip thickness
LIP_CLR   = 0.2    # lip <-> inner wall fit gap

USB_Y_K   = 10.0           # KiCad Y of USB-C centre
USB_W     = 9.6            # opening width  (receptacle 8.94)
USB_HGT   = 4.4            # opening height (receptacle 3.26, + tolerance)
USB_Z     = 1.9            # USB centre above PCB top (XIAO total 3.5 mm)  VERIFY

AUX_Y_K   = 8.8            # KiCad Y of jack centre
AUX_D     = 7.0            # opening dia (PJ-320A nose D5.6 + print tolerance)
AUX_Z     = 2.5            # jack centre above PCB top (PJ320 datasheet: body 6x5, nose D5)

LEDS_K    = [(11.33, 23.6), (18.95, 23.6)]
LED_D     = 2.0            # lid window dia

STANDOFF_D     = 3.0
STANDOFF_INSET = 2.5       # from PCB corner
# --------------------------------------------------

def cm(v): return v / 10.0          # Fusion API works in cm
def fy(yk): return PCB_H - yk       # KiCad Y -> Fusion Y

tb = adsk.fusion.TemporaryBRepManager.get()
P = adsk.core.Point3D.create
V = adsk.core.Vector3D.create

def box(x0, y0, z0, x1, y1, z1):
    c = P(cm((x0 + x1) / 2), cm((y0 + y1) / 2), cm((z0 + z1) / 2))
    obb = adsk.core.OrientedBoundingBox3D.create(
        c, V(1, 0, 0), V(0, 1, 0),
        cm(abs(x1 - x0)), cm(abs(y1 - y0)), cm(abs(z1 - z0)))
    return tb.createBox(obb)

def cyl(p1, p2, d):
    r = cm(d / 2)
    return tb.createCylinderOrCone(P(*map(cm, p1)), r, P(*map(cm, p2)), r)

def cut(t, tool):   tb.booleanOperation(t, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType)
def union(t, tool): tb.booleanOperation(t, tool, adsk.fusion.BooleanTypes.UnionBooleanType)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = design.rootComponent

        # derived geometry
        ix0, iy0 = -CLR, -CLR
        ix1, iy1 = PCB_W + CLR, PCB_H + CLR
        ox0, oy0 = ix0 - WALL, iy0 - WALL
        ox1, oy1 = ix1 + WALL, iy1 + WALL
        pcb_bot = FLOOR + STANDOFF
        pcb_top = pcb_bot + PCB_T
        base_top = pcb_top + PARTS_H + TOP_GAP

        # ---------- BASE ----------
        base = box(ox0, oy0, 0, ox1, oy1, base_top)
        cut(base, box(ix0, iy0, FLOOR, ix1, iy1, base_top + 1))
        for sx, sy in [(STANDOFF_INSET, STANDOFF_INSET),
                       (PCB_W - STANDOFF_INSET, STANDOFF_INSET),
                       (STANDOFF_INSET, PCB_H - STANDOFF_INSET),
                       (PCB_W - STANDOFF_INSET, PCB_H - STANDOFF_INSET)]:
            union(base, cyl((sx, sy, FLOOR - 0.1), (sx, sy, pcb_bot), STANDOFF_D))
        # USB-C opening, left wall
        uy, uz = fy(USB_Y_K), pcb_top + USB_Z
        cut(base, box(ox0 - 1, uy - USB_W / 2, uz - USB_HGT / 2,
                      ix0 + 1, uy + USB_W / 2, uz + USB_HGT / 2))
        # AUX opening, right wall
        ay, az = fy(AUX_Y_K), pcb_top + AUX_Z
        cut(base, cyl((ix1 - 1, ay, az), (ox1 + 1, ay, az), AUX_D))

        # ---------- LID ----------
        lid = box(ox0, oy0, base_top, ox1, oy1, base_top + LID_T)
        lx0, ly0 = ix0 + LIP_CLR, iy0 + LIP_CLR
        lx1, ly1 = ix1 - LIP_CLR, iy1 - LIP_CLR
        lip = box(lx0, ly0, base_top - LIP_H, lx1, ly1, base_top + 0.01)
        cut(lip, box(lx0 + LIP_W, ly0 + LIP_W, base_top - LIP_H - 1,
                     lx1 - LIP_W, ly1 - LIP_W, base_top + 1))
        union(lid, lip)
        for lxk, lyk in LEDS_K:
            x, y = lxk, fy(lyk)
            cut(lid, cyl((x, y, base_top - LIP_H - 1), (x, y, base_top + LID_T + 1), LED_D))

        # ---------- PCB reference (for fit check) ----------
        pcb = box(0, 0, pcb_bot, PCB_W, PCB_H, pcb_top)

        for name, body in [("Base", base), ("Lid", lid), ("PCB_ref", pcb)]:
            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            occ.component.name = name
            occ.component.bRepBodies.add(body).name = name

        ui.messageBox(
            "EarScope enclosure created.\n"
            f"Outer: {ox1-ox0:.1f} x {oy1-oy0:.1f} x {base_top+LID_T:.1f} mm\n"
            "Lid is in assembled position - hide it to see inside.")
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
