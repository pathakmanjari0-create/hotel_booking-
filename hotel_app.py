

import datetime
import random
import tkinter as tk
from pathlib import Path

# ------------------------------------------------------------------ theme
W, H = 1280, 800
NAV_H = 70
CH = H - NAV_H
IMG_DIR = Path(__file__).resolve().parent.parent / "images"

BG = "#f7f5f0"        # must match BG / CARD in tools/make_images.py (baked into photo corners)
CARD = "#ffffff"
TILE = "#f2efe8"
LINE = "#e3ddd2"
SHADOW = "#ebe6dc"
INPUT = "#fbfaf7"
INK = "#18232a"
MUTED = "#66707a"
DIM = "#a7adb2"
ACCENT = "#1e5f5a"
ACCENT_HI = "#277a73"
GOLD = "#c27c2c"
GREEN = "#2f8f5b"
WHITE = "#ffffff"

SERIF = "Georgia"
SANS = "Segoe UI"


def font(size, weight="normal"):
    return (SANS, -size, "bold" if weight in ("semi", "bold") else "normal")


def num(size):
    return (SANS, -round(size * 0.85), "bold")


def serif(size):
    return (SERIF, -int(size * 0.75), "bold")


# ------------------------------------------------------------------ data  (keep in sync with web/index.html)
ROOMS = [
    dict(img="double", name="Classic Double", kind="Room", price=3499, cap=2,
         rating=4.5, reviews=318, info="Queen bed  ·  24 m²  ·  City view"),
    dict(img="tallinn", name="Garden Twin", kind="Room", price=3799, cap=2,
         rating=4.6, reviews=204, info="2 single beds  ·  26 m²  ·  Garden view"),
    dict(img="twin", name="Deluxe Twin", kind="Room", price=4999, cap=2,
         rating=4.8, reviews=176, info="2 queen beds  ·  32 m²  ·  Lawn view"),
    dict(img="king", name="Deluxe King", kind="Room", price=5999, cap=2,
         rating=4.8, reviews=241, info="King bed  ·  36 m²  ·  Work desk"),
    dict(img="cleveland", name="Family Suite", kind="Suite", price=7999, cap=4,
         rating=4.7, reviews=93, info="2 double beds  ·  44 m²  ·  Sofa lounge"),
    dict(img="suite", name="Executive Suite", kind="Suite", price=11999, cap=3,
         rating=4.9, reviews=68, info="King bed  ·  68 m²  ·  Separate living room"),
]
BREAKFAST = 650          # per guest per night
OWNERS = "manjari pathak . shivang"


def gst_rate(room):
    """Indian hotel GST: 12% up to ₹7,500 a night, 18% above."""
    return 0.18 if room["price"] > 7500 else 0.12


def quote(room, guests, nights, breakfast):
    """(room line, room total, breakfast total, gst, grand total). Rooms are priced per room per night."""
    stay = room["price"] * nights
    bf = BREAKFAST * guests * nights if breakfast else 0
    gst = round((stay + bf) * gst_rate(room))
    label = f"₹{room['price']:,} × {nights} night{'s' if nights > 1 else ''}"
    return label, stay, bf, gst, stay + bf + gst


# ------------------------------------------------------------------ drawing helpers
def rr_points(x0, y0, x1, y1, r):
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    return [x0 + r, y0, x0 + r, y0, x1 - r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
            x1, y0 + r, x1, y1 - r, x1, y1 - r, x1, y1, x1 - r, y1, x1 - r, y1,
            x0 + r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y1 - r, x0, y0 + r,
            x0, y0 + r, x0, y0]


def rrect(cv, x0, y0, x1, y1, r, **kw):
    return cv.create_polygon(rr_points(x0, y0, x1, y1, r), smooth=True, **kw)


def hover_cursor(cv, tag):
    cv.tag_bind(tag, "<Enter>", lambda e: cv.config(cursor="hand2"), add="+")
    cv.tag_bind(tag, "<Leave>", lambda e: cv.config(cursor=""), add="+")


def after_text(cv, item, gap=6):
    """x just right of a text item, for putting a second colour/size on the same line."""
    return cv.bbox(item)[2] + gap


# ------------------------------------------------------------------ widgets
class Btn:
    STYLES = {
        "solid": (ACCENT, ACCENT_HI, "", WHITE),
        "light": (WHITE, "#e6eeed", "", INK),
        "soft": (TILE, LINE, LINE, INK),
    }

    def __init__(self, cv, x, y, w, h, text, cmd, style="solid", r=None, size=14, tags=()):
        fill, hover, outline, fg = self.STYLES[style]
        tag = f"btn{id(self)}"
        T = tuple(tags) + (tag,)
        bg = rrect(cv, x, y, x + w, y + h, h / 2 if r is None else r, fill=fill, outline=outline, width=1, tags=T)
        cv.create_text(x + w / 2, y + h / 2, text=text, fill=fg, font=font(size, "semi"), tags=T)
        cv.tag_bind(tag, "<Enter>", lambda e: cv.itemconfigure(bg, fill=hover))
        cv.tag_bind(tag, "<Leave>", lambda e: cv.itemconfigure(bg, fill=fill))
        cv.tag_bind(tag, "<Button-1>", lambda e: cmd())
        hover_cursor(cv, tag)


class Choice:
    """Row/grid of option tiles; one is selected."""

    def __init__(self, cv, rects, labels, on_change=None, selected=0, r=10, size=13, tags=()):
        self.cv, self.sel, self.on_change = cv, selected, on_change
        self.tiles = []
        for i, (rc, label) in enumerate(zip(rects, labels)):
            t = f"ch{id(self)}_{i}"
            box = rrect(cv, *rc, r, width=1, tags=tuple(tags) + (t,))
            txt = cv.create_text((rc[0] + rc[2]) / 2, (rc[1] + rc[3]) / 2, text=label, justify="center",
                                 font=font(size, "semi"), tags=tuple(tags) + (t,))
            self.tiles.append((box, txt))
            cv.tag_bind(t, "<Button-1>", lambda e, i=i: self.select(i))
            hover_cursor(cv, t)
        self._paint()

    def _paint(self):
        for i, (box, txt) in enumerate(self.tiles):
            on = i == self.sel
            self.cv.itemconfigure(box, fill=ACCENT if on else TILE, outline="" if on else LINE)
            self.cv.itemconfigure(txt, fill=WHITE if on else INK)

    def select(self, i):
        self.sel = i
        self._paint()
        if self.on_change:
            self.on_change(i)


class Field:
    """Text input with placeholder."""

    def __init__(self, cv, x, y, w, h, placeholder, tags=()):
        self.ph = placeholder
        self.frame = tk.Frame(cv, bg=INPUT, highlightthickness=1, highlightbackground=LINE)
        self.e = tk.Entry(self.frame, bg=INPUT, fg=DIM, insertbackground=INK, relief="flat", bd=0,
                          font=font(14), highlightthickness=0)
        self.e.pack(fill="both", expand=True, padx=12, pady=6)
        self.e.insert(0, placeholder)
        self.empty = True
        self.e.bind("<FocusIn>", self._in)
        self.e.bind("<FocusOut>", self._out)
        cv.create_window(x, y, window=self.frame, width=w, height=h, anchor="nw", tags=tags)

    def _in(self, e):
        self.frame.config(highlightbackground=ACCENT)
        if self.empty:
            self.e.delete(0, "end")
            self.e.config(fg=INK)
            self.empty = False

    def _out(self, e):
        self.frame.config(highlightbackground=LINE)
        if not self.e.get().strip():
            self.e.delete(0, "end")
            self.e.insert(0, self.ph)
            self.e.config(fg=DIM)
            self.empty = True

    def value(self):
        return "" if self.empty else self.e.get().strip()


# ------------------------------------------------------------------ pages
CARD_W, CARD_H, GAP = 366, 356, 21


class Page(tk.Canvas):
    def __init__(self, app, content_h=CH):
        super().__init__(app, width=W, height=CH, bg=BG, highlightthickness=0, bd=0, yscrollincrement=20)
        self.app = app
        self.set_height(content_h)

    def set_height(self, content_h):
        self.content_h = content_h
        self.config(scrollregion=(0, 0, W, max(CH, content_h)))

    def wheel(self, delta):
        if self.content_h > CH:
            self.yview_scroll(-3 if delta > 0 else 3, "units")

    def heading(self, title, sub):
        self.create_text(70, 50, text=title, anchor="w", font=serif(42), fill=INK)
        self.create_text(72, 88, text=sub, anchor="w", font=font(14), fill=MUTED)

    def card(self, x0, y0, x1, y1, title=None, r=18, tags=()):
        rrect(self, x0, y0 + 4, x1, y1 + 4, r, fill=SHADOW, outline="", tags=tags)
        rrect(self, x0, y0, x1, y1, r, fill=CARD, outline=LINE, width=1, tags=tags)
        if title:
            self.create_text(x0 + 24, y0 + 32, text=title, anchor="w", font=serif(24), fill=INK, tags=tags)

    def stars(self, x, y, room, anchor_right=False, tags=()):
        """'★ 4.8 (289)' with the star+score in gold and the count muted."""
        a = self.create_text(x, y, text=f"★ {room['rating']}", anchor="w", font=font(13, "semi"), fill=GOLD,
                             tags=tags)
        b = self.create_text(after_text(self, a, 4), y, text=f"({room['reviews']})", anchor="w", font=font(12),
                             fill=MUTED, tags=tags)
        if anchor_right:
            dx = x - after_text(self, b, 0)
            self.move(a, dx, 0)
            self.move(b, dx, 0)

    def room_card(self, x, y, i, tags=()):
        room = ROOMS[i]
        self.card(x, y, x + CARD_W, y + CARD_H, r=16, tags=tags)
        self.create_image(x + 8, y + 8, image=self.app.img[room["img"] + "_card"], anchor="nw", tags=tags)
        rrect(self, x + 18, y + 18, x + 98, y + 44, 13, fill=WHITE, outline="", tags=tags)
        self.create_text(x + 58, y + 31, text=room["kind"].upper(), font=font(11, "bold"), fill=ACCENT, tags=tags)

        self.create_text(x + 20, y + 236, text=room["name"], anchor="w", font=serif(22), fill=INK, tags=tags)
        self.stars(x + CARD_W - 20, y + 237, room, anchor_right=True, tags=tags)
        self.create_text(x + 20, y + 264, text=room["info"], anchor="w", font=font(13), fill=MUTED, tags=tags)
        self.create_line(x + 20, y + 292, x + CARD_W - 20, y + 292, fill=LINE, tags=tags)
        p = self.create_text(x + 20, y + 325, text=f"₹{room['price']:,}", anchor="w", font=num(26), fill=INK,
                             tags=tags)
        self.create_text(after_text(self, p), y + 328, text="/ night", anchor="w", font=font(13),
                         fill=MUTED, tags=tags)
        Btn(self, x + CARD_W - 108, y + 307, 88, 38, "Book", lambda: self.app.book(i), r=10, size=13, tags=tags)


STATS = [("4.8 ★", "Average guest rating"), ("24/7", "Room service and concierge"),
         ("Free", "Wi-Fi and airport pickup"), ("₹3,499", "Rooms from, per night")]
AMENITIES = ["Free Wi-Fi", "Room service", "Spa", "Fitness centre", "Airport pickup", "Valet parking",
             "Laundry"]
FEATURED = [3, 5, 2]
HOME_H = 1740


class HomePage(Page):
    def __init__(self, app):
        super().__init__(app, HOME_H)
        a = app
        # ---------- hero ----------
        self.create_image(0, 0, image=a.img["hero"], anchor="nw")
        Btn(self, 72, 336, 156, 48, "View rooms", lambda: a.show("Rooms"))
        Btn(self, 240, 336, 156, 48, "Book a stay", lambda: a.show("Book"), style="light")

        # ---------- stats bar overlapping the hero ----------
        self.card(70, 418, 1210, 518, r=16)
        cw = (1210 - 70) / len(STATS)
        for k, (big, small) in enumerate(STATS):
            cx = 70 + cw * k + cw / 2
            self.create_text(cx, 456, text=big, font=num(28), fill=ACCENT)
            self.create_text(cx, 486, text=small, font=font(13), fill=MUTED)
            if k:
                self.create_line(70 + cw * k, 440, 70 + cw * k, 496, fill=LINE)

        # ---------- popular rooms ----------
        y = 590
        self.create_text(68, y, text="Popular rooms", anchor="w", font=serif(40), fill=INK)
        self.create_text(1210, y + 4, text="See all rooms  →", anchor="e", font=font(15, "semi"), fill=ACCENT,
                         tags="allrooms")
        self.tag_bind("allrooms", "<Button-1>", lambda e: a.show("Rooms"))
        hover_cursor(self, "allrooms")
        for k, i in enumerate(FEATURED):
            self.room_card(70 + k * (CARD_W + GAP), y + 40, i)

        # ---------- facilities ----------
        y = 1070
        self.create_text(68, y, text="Hotel facilities", anchor="w", font=serif(40), fill=INK)
        self.create_text(70, y + 40, text="Dine, swim and unwind without leaving the hotel.",
                         anchor="w", font=font(15), fill=MUTED)
        for k, (img, title, sub) in enumerate((
                ("restaurant", "The Courtyard restaurant", "All-day dining. Breakfast buffet 7 – 10:30 AM."),
                ("pool", "Outdoor pool", "Heated pool and sun deck, open 7 AM – 9 PM."))):
            x = 70 + k * 585
            self.create_image(x, y + 74, image=a.img[img], anchor="nw")
            self.create_text(x + 2, y + 404, text=title, anchor="w", font=serif(24), fill=INK)
            self.create_text(x + 2, y + 432, text=sub, anchor="w", font=font(14), fill=MUTED)

        x, y = 70, y + 490
        for name in AMENITIES:
            t = self.create_text(x + 18, y, text=f"✓  {name}", anchor="w", font=font(13, "semi"), fill=INK)
            x1 = after_text(self, t, 18)
            pill = rrect(self, x, y - 18, x1, y + 18, 18, fill=CARD, outline=LINE)
            self.tag_lower(pill, t)
            x = x1 + 12

        # ---------- footer ----------
        y = HOME_H - 110
        self.create_line(70, y, 1210, y, fill=LINE)
        self.create_text(640, y + 34, text="Hotel Booking  ·  Check-in 2 PM  ·  Check-out 12 PM  ·  Front desk open 24/7",
                         font=font(13), fill=MUTED)
        self.create_text(640, y + 60, text=f"Owners: {OWNERS}", font=font(12), fill=DIM)


class RoomsPage(Page):
    FILTERS = ["All", "Rooms", "Suites"]

    def __init__(self, app):
        super().__init__(app)
        self.heading("Rooms & suites", "Prices are per room, per night. GST is added at booking.")
        rects = [(914 + k * 100, 32, 1010 + k * 100, 72) for k in range(3)]
        Choice(self, rects, self.FILTERS, on_change=self.draw, size=14)
        self.draw(0)

    def draw(self, f):
        self.delete("grid")
        show = [i for i, r in enumerate(ROOMS) if f == 0 or r["kind"] == ("Room", "Suite")[f - 1]]
        for k, i in enumerate(show):
            self.room_card(70 + (k % 3) * (CARD_W + GAP), 130 + (k // 3) * (CARD_H + 26), i, tags=("grid",))
        rows = (len(show) + 2) // 3
        self.set_height(130 + rows * (CARD_H + 26) + 40)
        self.yview_moveto(0)


class BookPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.heading("Book your stay", "Pick a room, dates and guests. Pay at the hotel, no card needed.")
        self.guests, self.nights = 2, 2
        today = datetime.date.today()
        self.dates = [today + datetime.timedelta(days=i) for i in range(7)]

        # ---------- left: room, dates, nights, guests, breakfast ----------
        self.card(70, 120, 760, 700)
        self.thumb = self.create_image(94, 144, anchor="nw")
        self.r_kind = self.create_text(370, 160, anchor="w", font=font(12, "bold"), fill=ACCENT)
        self.r_name = self.create_text(368, 192, anchor="w", font=serif(30), fill=INK)
        self.r_info = self.create_text(370, 226, anchor="w", font=font(13), fill=MUTED)
        self.r_price = self.create_text(370, 286, anchor="w", font=num(26), fill=INK)
        self.r_unit = self.create_text(0, 289, text="/ night", anchor="w", font=font(13), fill=MUTED)

        self.create_text(94, 340, text="Room", anchor="w", font=serif(20), fill=INK)
        rects = [(94 + (i % 3) * 218, 360 + (i // 3) * 50, 94 + (i % 3) * 218 + 208, 360 + (i // 3) * 50 + 42)
                 for i in range(len(ROOMS))]
        self.room_choice = Choice(self, rects, [r["name"] for r in ROOMS], on_change=lambda i: self.update())

        self.create_text(94, 484, text="Check-in", anchor="w", font=serif(20), fill=INK)
        rects = [(94 + i * 92, 504, 94 + i * 92 + 84, 562) for i in range(7)]
        labels = [("Today" if i == 0 else d.strftime("%a")) + f"\n{d.day} {d.strftime('%b')}"
                  for i, d in enumerate(self.dates)]
        self.date_choice = Choice(self, rects, labels, on_change=lambda i: self.update(), size=13)

        self.counters = {}
        for x, label, attr in ((94, "Nights", "nights"), (300, "Guests", "guests")):
            self.create_text(x, 600, text=label, anchor="w", font=serif(20), fill=INK)
            Btn(self, x, 620, 44, 44, "−", lambda a=attr: self.step(a, -1), style="soft", size=18)
            self.counters[attr] = self.create_text(x + 76, 642, font=font(18, "bold"), fill=INK)
            Btn(self, x + 108, 620, 44, 44, "+", lambda a=attr: self.step(a, 1), style="soft", size=18)
        self.cap_txt = self.create_text(452, 600, anchor="e", font=font(12), fill=DIM)

        self.create_text(500, 600, text="Breakfast", anchor="w", font=serif(20), fill=INK)
        self.bf_choice = Choice(self, [(500, 620, 614, 664), (622, 620, 736, 664)], ["Room only", "Included"],
                                on_change=lambda i: self.update(), size=13)

        # ---------- right: details and price ----------
        self.card(790, 120, 1210, 700, "Your details")
        self.name = Field(self, 814, 176, 372, 46, "Full name")
        self.phone = Field(self, 814, 236, 372, 46, "Phone number")
        self.email = Field(self, 814, 296, 372, 46, "Email (optional)")
        self.create_line(814, 362, 1186, 362, fill=LINE)
        self.rows = []
        for y in (390, 420, 450):
            self.rows.append((self.create_text(814, y, anchor="w", font=font(14), fill=MUTED),
                              self.create_text(1186, y, anchor="e", font=font(14, "semi"), fill=INK)))
        self.create_line(814, 476, 1186, 476, fill=LINE)
        self.create_text(814, 510, text="Total", anchor="w", font=serif(28), fill=INK)
        self.total_val = self.create_text(1186, 510, anchor="e", font=num(36), fill=ACCENT)
        self.summary = self.create_text(814, 552, anchor="w", font=font(14, "semi"), fill=ACCENT, width=372)
        self.create_text(814, 588, text="Free cancellation up to 24 hours before check-in.", anchor="w",
                         font=font(12), fill=MUTED)
        Btn(self, 814, 620, 372, 52, "Confirm booking", self.confirm, size=16)
        self.update()

    @property
    def room(self):
        return ROOMS[self.room_choice.sel]

    def select_room(self, i):
        self.room_choice.select(i)

    def step(self, attr, d):
        hi = self.room["cap"] if attr == "guests" else 14
        setattr(self, attr, max(1, min(hi, getattr(self, attr) + d)))
        self.update()

    def stay_text(self):
        d0 = self.dates[self.date_choice.sel]
        d1 = d0 + datetime.timedelta(days=self.nights)
        g = self.guests
        return f"{d0.strftime('%a, %d %b')}  →  {d1.strftime('%a, %d %b')}  ·  {g} guest{'s' if g > 1 else ''}"

    def quote(self):
        return quote(self.room, self.guests, self.nights, self.bf_choice.sel == 1)

    def update(self):
        room = self.room
        self.guests = min(self.guests, room["cap"])
        self.itemconfigure(self.thumb, image=self.app.img[room["img"] + "_thumb"])
        self.itemconfigure(self.r_kind, text=room["kind"].upper())
        self.itemconfigure(self.r_name, text=room["name"])
        self.itemconfigure(self.r_info, text=room["info"])
        self.delete("rstars")
        self.stars(370, 254, room, tags=("rstars",))
        self.itemconfigure(self.r_price, text=f"₹{room['price']:,}")
        self.coords(self.r_unit, after_text(self, self.r_price), 289)
        self.itemconfigure(self.cap_txt, text=f"max {room['cap']}")
        for attr, item in self.counters.items():
            self.itemconfigure(item, text=str(getattr(self, attr)))

        label, stay, bf, gst, total = self.quote()
        rows = [(label, f"₹{stay:,}"),
                (f"Breakfast  ₹{BREAKFAST} × {self.guests} × {self.nights}" if bf else "Breakfast",
                 f"₹{bf:,}" if bf else "—"),
                (f"GST ({round(gst_rate(room) * 100)}%)", f"₹{gst:,}")]
        for (lbl, val), (a, b) in zip(rows, self.rows):
            self.itemconfigure(a, text=lbl)
            self.itemconfigure(b, text=val)
        self.itemconfigure(self.total_val, text=f"₹{total:,}")
        self.itemconfigure(self.summary, text=self.stay_text())

    def confirm(self):
        phone = re.sub(r"\D", "", self.phone.value())
        email = self.email.value()
        if not self.name.value():
            self.app.toast("Please add your name")
        elif not 10 <= len(phone) <= 13:
            self.app.toast("Please add a valid phone number")
        elif email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            self.app.toast("That email doesn't look right")
        else:
            self.app.confirm("Booking confirmed", f"We look forward to welcoming you, {self.name.value().split()[0]}",
                             f"Booking #HB-{random.randint(10000, 99999)}\n{self.room['name']}  ·  {self.stay_text()}\n"
                             f"Total ₹{self.quote()[4]:,}, pay at the hotel")


# ------------------------------------------------------------------ app
class App(tk.Tk):
    TABS = ["Home", "Rooms", "Book"]

    def __init__(self):
        super().__init__()
        self.title("Hotel Booking")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{max(0, (sw - W) // 2)}+{max(0, (sh - H) // 2 - 30)}")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.modal = None
        self.toast_lbl = None
        self.img = {p.stem: tk.PhotoImage(file=str(p)) for p in IMG_DIR.glob("*.png")}

        self._build_nav()
        self.pages = {"Home": HomePage(self), "Rooms": RoomsPage(self), "Book": BookPage(self)}
        for p in self.pages.values():
            p.place(x=0, y=NAV_H)
        self.current = None
        self.show("Home")
        self.bind_all("<MouseWheel>", lambda e: self._wheel_delta(e.delta))
        for key, d in (("<Next>", -360), ("<Prior>", 360), ("<Down>", -120), ("<Up>", 120)):
            self.bind(key, lambda e, d=d: self._wheel_delta(d))

    def _wheel_delta(self, d):
        if not self.modal and not isinstance(self.focus_get(), tk.Entry):
            self.pages[self.current].wheel(d)

    # ---------- nav ----------
    def _build_nav(self):
        nv = self.nav = tk.Canvas(self, width=W, height=NAV_H, highlightthickness=0, bd=0, bg=CARD)
        nv.place(x=0, y=0)
        nv.create_line(0, NAV_H - 1, W, NAV_H - 1, fill=LINE)
        rrect(nv, 70, 19, 102, 51, 9, fill=ACCENT, outline="", tags="logo")
        nv.create_text(86, 35, text="H", font=serif(24), fill=WHITE, tags="logo")
        nv.create_text(114, NAV_H / 2, text="Hotel Booking", anchor="w", font=serif(30), fill=INK, tags="logo")
        nv.tag_bind("logo", "<Button-1>", lambda e: self.show("Home"))
        hover_cursor(nv, "logo")

        self.tab_items = {}
        x = 520
        for name in self.TABS:
            t = nv.create_text(x, NAV_H / 2, text=name, font=font(15, "semi"), fill=MUTED, tags=f"tab_{name}")
            self.tab_items[name] = t
            nv.tag_bind(f"tab_{name}", "<Button-1>", lambda e, n=name: self.show(n))
            hover_cursor(nv, f"tab_{name}")
            x += 120
        self.tab_bar = nv.create_line(0, 0, 0, 0, fill=ACCENT, width=2)
        Btn(nv, 1080, 15, 130, 40, "Book now", lambda: self.show("Book"), size=14)

    def show(self, name):
        self.close_modal()
        if name == self.current:
            return
        self.current = name
        tk.Misc.lift(self.pages[name])
        for n, item in self.tab_items.items():
            self.nav.itemconfigure(item, fill=INK if n == name else MUTED)
        x0, _, x1, _ = self.nav.bbox(self.tab_items[name])
        self.nav.coords(self.tab_bar, x0, NAV_H - 14, x1, NAV_H - 14)

    def book(self, i):
        self.pages["Book"].select_room(i)
        self.show("Book")

    # ---------- toast ----------
    def toast(self, text):
        if self.toast_lbl:
            self.toast_lbl.destroy()
        lbl = self.toast_lbl = tk.Label(self, text=text, bg=INK, fg=WHITE, font=font(14, "semi"), padx=22, pady=10)
        lbl.place(relx=0.5, y=H - 30, anchor="s")
        self.after(2000, lambda: lbl.winfo_exists() and lbl.destroy())

    # ---------- confirmation popup ----------
    def confirm(self, title, line1, details):
        self.close_modal()
        cv = self.modal = tk.Canvas(self, width=W, height=H, bg="#1c262b", highlightthickness=0, bd=0)
        cv.place(x=0, y=0)
        pw, ph = 540, 360
        px, py = (W - pw) // 2, (H - ph) // 2
        rrect(cv, px, py, px + pw, py + ph, 22, fill=CARD, outline="", width=1)
        cx = px + pw / 2
        cv.create_oval(cx - 30, py + 30, cx + 30, py + 90, fill="#e2f1e8", outline="")
        cv.create_text(cx, py + 60, text="✓", font=font(30, "bold"), fill=GREEN)
        cv.create_text(cx, py + 130, text=title, font=serif(34), fill=INK)
        cv.create_text(cx, py + 168, text=line1, font=font(15, "semi"), fill=ACCENT)
        cv.create_text(cx, py + 226, text=details, font=font(13), fill=MUTED, justify="center", width=480)
        Btn(cv, cx - 80, py + ph - 70, 160, 46, "Done", self.close_modal, size=15)
        self.bind("<Escape>", lambda e: self.close_modal())

    def close_modal(self):
        if self.modal:
            self.modal.destroy()
            self.modal = None
            self.unbind("<Escape>")


def selftest():
    double, suite = ROOMS[0], ROOMS[5]
    assert quote(double, 2, 3, False)[1:] == (3499 * 3, 0, round(3499 * 3 * 0.12), 3499 * 3 + round(3499 * 3 * 0.12))
    stay, bf = 11999 * 2, 650 * 3 * 2
    assert quote(suite, 3, 2, True)[1:] == (stay, bf, round((stay + bf) * 0.18), stay + bf + round((stay + bf) * 0.18))
    assert quote(double, 1, 1, False)[0] == "₹3,499 × 1 night"
    assert all((IMG_DIR / f"{r['img']}_{s}.png").exists() for r in ROOMS for s in ("card", "thumb"))
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else App().mainloop()
