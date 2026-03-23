/**
 * This is free and unencumbered software released into the public domain.
 *
 * Anyone is free to copy, modify, publish, use, compile, sell, or
 * distribute this software, either in source code form or as a compiled
 * binary, for any purpose, commercial or non-commercial, and by any
 * means.
 *
 * In jurisdictions that recognize copyright laws, the author or authors
 * of this software dedicate any and all copyright interest in the
 * software to the public domain. We make this dedication for the benefit
 * of the public at large and to the detriment of our heirs and
 * successors. We intend this dedication to be an overt act of
 * relinquishment in perpetuity of all present and future rights to this
 * software under copyright law.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
 * For more information, please refer to <https://unlicense.org/>
 */

#include <X11/Xlib.h>
#include <X11/Xutil.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FLAG_RGBA (1 << 0)

static int red_max   = 0, red_shift;
static int green_max = 0, green_shift;
static int blue_max  = 0, blue_shift;

static unsigned long generate_color(Display* display, unsigned long r, unsigned long g, unsigned long b) {
	unsigned long c = 0;

	if(red_max == 0) {
		XColor xc;

		xc.red	 = r * 256;
		xc.green = g * 256;
		xc.blue	 = b * 256;
		XAllocColor(display, DefaultColormap(display, DefaultScreen(display)), &xc);

		c = xc.pixel;
	} else {
		c |= (r * red_max / 255) << red_shift;

		c |= (g * green_max / 255) << green_shift;

		c |= (b * blue_max / 255) << blue_shift;
	}

	return c;
}

static XVisualInfo* get_visual_info(Display* display) {
	XVisualInfo xvi;
	int	    n;
	Visual*	    visual = DefaultVisual(display, DefaultScreen(display));

	xvi.visualid = XVisualIDFromVisual(visual);

	return XGetVisualInfo(display, VisualIDMask, &xvi, &n);
}

int main(int argc, char** argv) {
	FILE*		  in;
	XVisualInfo*	  xvi;
	int		  width, height, size;
	char		  sig[2];
	unsigned char	  flag;
	unsigned char	  dword[4];
	int		  i, j, k;
	Display*	  display;
	Window		  wnd;
	GC		  gc;
	int		  bpp; /* BYTE per pixel */
	Atom		  wm_protocols, wm_delete_window;
	char		  title[2048];
	XImage*		  image;
	XWindowAttributes attr;
	unsigned char	  defcolor[3] = {0, 0, 0};

	if((in = fopen(argv[1], "rb")) == NULL) return 1;
	if((display = XOpenDisplay(NULL)) == NULL) return 1;

	sprintf(title, "xswzl2: %s", argv[1]);

	fseek(in, 0, SEEK_END);
	size = ftell(in);
	fseek(in, 0, SEEK_SET);

	if(fread(sig, 1, 2, in) < 2 || memcmp(sig, "SM", 2) != 0) return 1;

	fread(&flag, 1, 1, in);
	if(flag & FLAG_RGBA) {
		bpp = 4;
	} else {
		bpp = 3;
	}

	fread(dword, 1, 4, in);
	for(i = 0; i < 4; i++) {
		width = width << 8;
		width = width | dword[3 - i];
	}

	height = (size - 2 - 1 - 4) / bpp / width;

	xvi = get_visual_info(display);

	if(xvi->red_mask != 0) {
#define COLOR(name) \
	{ \
		i = 0; \
		while(!((1 << i) & xvi->name##_mask)) i++; \
		name##_max   = xvi->name##_mask >> i; \
		name##_shift = i; \
	}

		COLOR(red);
		COLOR(green);
		COLOR(blue);

#undef COLOR
	}

	wnd = XCreateSimpleWindow(display, DefaultRootWindow(display), 0, 0, width, height, 0, 0, WhitePixel(display, DefaultScreen(display)));
	XSetStandardProperties(display, wnd, title, "xswzl2", None, (char**)NULL, 0, NULL);

	wm_protocols	 = XInternAtom(display, "WM_PROTOCOLS", False);
	wm_delete_window = XInternAtom(display, "WM_DELETE_WINDOW", False);
	XSetWMProtocols(display, wnd, &wm_delete_window, 1);

	XGetWindowAttributes(display, DefaultRootWindow(display), &attr);

	image	    = XCreateImage(display, DefaultVisual(display, DefaultScreen(display)), attr.depth, ZPixmap, 0, NULL, width, height, 32, 0);
	image->data = malloc(image->bytes_per_line * height);

	for(i = 0; i < height; i++) {
		for(j = 0; j < width; j++) {
			unsigned char pi[4];
			unsigned long p;

			fread(pi, 1, bpp, in);
			if(bpp == 3) pi[3] = 255;

			for(k = 0; k < 3; k++) {
				pi[k] = pi[k] * pi[3] / 255;
				pi[k] += defcolor[k] * (255 - pi[3]) / 255;
			}

			p = generate_color(display, pi[0], pi[1], pi[2]);

			XPutPixel(image, j, i, p);
		}
	}

	gc = XCreateGC(display, wnd, 0, NULL);

	XSelectInput(display, wnd, ExposureMask);

	XMapWindow(display, wnd);

	while(1) {
		XEvent ev;

		XNextEvent(display, &ev);

		if(ev.type == Expose) {
			XImage* trimage;

			XGetWindowAttributes(display, wnd, &attr);

			trimage	      = XCreateImage(display, DefaultVisual(display, DefaultScreen(display)), attr.depth, ZPixmap, 0, NULL, attr.width, attr.height, 32, 0);
			trimage->data = malloc(trimage->bytes_per_line * trimage->height);

			for(i = 0; i < trimage->height; i++) {
				int fy = i * image->height / trimage->height;

				if(fy >= image->height) fy = image->height - 1;

				for(j = 0; j < trimage->width; j++) {
					int	      fx = j * image->width / trimage->width;
					unsigned long p;

					if(fx >= image->width) fx = image->width - 1;

					p = XGetPixel(image, fx, fy);
					XPutPixel(trimage, j, i, p);
				}
			}

			XPutImage(display, wnd, gc, trimage, 0, 0, 0, 0, trimage->width, trimage->height);

			XDestroyImage(trimage);
		} else if(ev.type == ClientMessage) {
			if(ev.xclient.message_type == wm_protocols && ev.xclient.data.l[0] == wm_delete_window) break;
		}
	}

	XDestroyImage(image);

	XCloseDisplay(display);
}
