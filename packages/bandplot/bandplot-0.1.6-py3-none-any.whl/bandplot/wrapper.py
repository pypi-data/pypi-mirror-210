import ast, argparse, os, re, platform, glob
import matplotlib.pyplot as plt
from bandplot import plots, pplots, readdata
from bandplot import __version__

plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['ytick.minor.visible'] = True
plt.rcParams["mathtext.fontset"] = 'cm'

class cla_fig:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, str):
                exec('self.%s = "%s"' %(key, value))
            else:
                exec('self.%s = %s' %(key, value))

# bandplot
def main():
    parser = argparse.ArgumentParser(description='Plot the band structure or DOS from vaspkit result.',
                                     epilog='''
Example:
bandplot -i BAND.dat -o BAND.png -l g m k g -d PDOS* -z -p C-s,p Ti-d
''',
    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', "--version",    action="version",     version="bandplot "+__version__+" from "+os.path.dirname(__file__)+' (python'+platform.python_version()+')')
    parser.add_argument('-s', "--size",       type=int,   nargs=2,  help='figure size: width, height', metavar=('width','height'))
    parser.add_argument('-b', "--divided",    action='store_true',  help="plot the up and down spin in divided subplot")
    parser.add_argument('-y', "--vertical",   type=float, nargs=2,  help="energy (eV) range, default: [-5.0, 5.0]", metavar=('start','end'))
    parser.add_argument('-g', "--legend",     type=str,             nargs='+', help="legend labels", default=[])
    parser.add_argument('-a', "--location",   type=str.lower,       nargs='+', help="arrange the legend location, default: best", default=[], metavar="str")
    parser.add_argument('-c', "--color",      type=str,             nargs='+', help="line color: b, blue; g, green; r, red; c, cyan; m, magenta; y, yellow;"+
                                                                                    "k, black; w, white", default=[], metavar="color")
    parser.add_argument('-k', "--linestyle",  type=str,             nargs='+', help="linestyle: solid, dashed, dashdot, dotted or tuple; default: solid",
                                                                                    default=[], metavar="str")
    parser.add_argument('-w', "--linewidth",  type=str,             nargs='+', help="linewidth, default: 0.8", default=[], metavar="0.8")
    parser.add_argument('-m', "--mass",       type=float,           nargs='?', help='calculate the effective masses, default: 0.15', default=None, const=0.15,
                                                                                    metavar="scale")
    parser.add_argument('-r', "--projected",  action='store_true',  help='plot the projected band structure')
    parser.add_argument('-i', "--input",      type=str,             nargs='+', help="plot figure from .dat file, default: BAND.dat", default=["BAND.dat"])
    parser.add_argument('-o', "--output",     type=str,             help="plot figure filename, default: BAND.png", default="BAND.png")
    parser.add_argument('-q', "--dpi",        type=int,             help="dpi of the figure, default: 500", default=500)
    parser.add_argument('-j', "--klabels",    type=str,             help="filename of KLABELS, default: KLABELS", default="KLABELS")
    parser.add_argument('-l', "--labels",     type=str.upper,       nargs='+', default=[], help='labels for high-symmetry points, such as X S Y K M')
    parser.add_argument('-d', "--dos",        type=str,             nargs='*', default=None, help="plot DOS from .dat file, or file list")
    parser.add_argument('-x', "--horizontal", type=float, nargs=2,  help="Density of states, electrons/eV range", metavar=('start','end'))
    parser.add_argument('-n', "--exchange",   action='store_true',  help="exchange the x and y axes of DOS")
    parser.add_argument('-p', "--partial",    type=str,             nargs='+', default=[], help='the partial DOS to plot, s p d, or symbol-s,p,d')
    parser.add_argument('-e', "--elements",   type=str,             nargs='+', default=[], help="PDOS labels")
    parser.add_argument('-W', "--wratios",    type=float,           help='width ratio for DOS subplot')
    parser.add_argument('-z', "--fill",       type=float,           nargs='?', help='fill a shaded region between PDOS and axis, default: 0.2', default=None,
                                                                                    const=0.2, metavar="alpha")
    parser.add_argument('-f', "--font",       type=str,             help="font to use", default='STIXGeneral')

    args = parser.parse_args()

    labels = [re.sub("'|‘|’", '′', re.sub('"|“|”', '″', re.sub('^GA[A-Z]+$|^G$', 'Γ', i))) for i in args.labels]
    elements = [re.sub("'|‘|’", '′', re.sub('"|“|”', '″', i)) for i in args.elements]
    if args.dos is not None:
        if args.dos == []:
            dosfiles = [f for f in glob.glob('PDOS*.dat')] or [f for f in glob.glob('TDOS.dat')]
        else:
            dosfiles = [f for i in args.dos for f in glob.glob(i)]
    else:
        dosfiles = None

    color = []
    for i in args.color:
        j = i.split('*')
        if len(j) == 2:
            color += [ast.literal_eval(j[0])] * int(j[1]) if '(' in j[0] and ')' in j[0] else [j[0]] * int(j[1])
        else:
            color += [ast.literal_eval(i)] if '(' in i and ')' in i else [i]

    linestyle = []
    for i in args.linestyle:
        j = i.split('*')
        if len(j) == 2:
            linestyle += [ast.literal_eval(j[0])] * int(j[1]) if '(' in j[0] and ')' in j[0] else [j[0]] * int(j[1])
        else:
            linestyle += [ast.literal_eval(i)] if '(' in i and ')' in i else [i]

    linewidth = []
    for i in args.linewidth:
        j = i.split('*')
        linewidth += [float(j[0])] * int(j[1]) if len(j) == 2 else [float(i)]

    plt.rcParams['font.family'] = '%s'%args.font

    pltname = os.path.split(os.getcwd())[-1]
    formula = ''
    if os.path.exists('POSCAR'):
        symbol, factor = readdata.symbols('POSCAR')
        for i in range(len(symbol)):
            if factor[i] > 1:
                formula = formula + symbol[i]
                for j in str(factor[i]):
                    formula = formula + '$_'+ j + '$'
            else:
                formula = formula + symbol[i]

    legend = args.legend or [formula] or [pltname]

    ticks   = []
    klabels = []
    if os.path.exists(args.klabels):
        ticks, klabels = readdata.klabels(args.klabels)

    if len(labels) == 0:
        labels=[re.sub('GAMMA|Gamma|G', 'Γ', re.sub('Undefined|Un|[0-9]', '', i)) for i in klabels]

    if len(ticks) > len(labels):
        labels += [''] * (len(ticks) - len(labels))
    elif len(ticks) < len(labels):
        labels = labels[:len(ticks)]

    width_ratios = args.wratios or (0.3 if args.divided else 0.5)
    location = [int(i) if i.isdigit() else i for i in args.location]

    fig_p = cla_fig(output=args.output, size=args.size, vertical=args.vertical, horizontal=args.horizontal,
                    color=color, linestyle=linestyle, linewidth=linewidth, location=location, dpi=args.dpi,
                    width_ratios=width_ratios, exchange=args.exchange, fill=args.fill)
# calculate the effective masses
    if args.mass is not None:
        if not fig_p.vertical:
            fig_p.vertical = [-5.0, 5.0]
        scale = 0.15 if args.mass > 0.75 or args.mass < 0.05 else args.mass
        from bandplot import mass
        if os.path.exists("BAND_GAP"):
            lumo, homo, homo_c, filename = mass.get_vbm_cbm("BAND_GAP")
            Extension = [len(lumo), len(homo), len(homo_c), len(filename)]
            if all(x == 1 for x in Extension):
                data = mass.bs_dat_read(filename)
                calM = mass.dat_read(data[0], lumo[0], homo[0], homo_c[0], scale)
                pltlabel = mass.npfit(calM)
                mass.plot(data[0], calM, pltlabel, ticks, labels, legend, fig_p)
                print("{:<8}{:<8}{:<8}{:<8}{:<8}{:<8}".format("e_x","e_y","h1_x","h1_y","h2_x","h2_y"))
                for i in pltlabel:
                    if isinstance(i, float):
                        print("{:<8.3f}".format(i), end='')
                    else:
                        print("{:<8s}".format('-'), end='')
                print()
            elif all(x == 2 for x in Extension):
                data = mass.bs_dat_read(filename)
                calM_u = mass.dat_read(data[0], lumo[0], homo[0], homo_c[0], scale)
                calM_d = mass.dat_read(data[1], lumo[1], homo[1], homo_c[1], scale)
                pltlabel_u = mass.npfit(calM_u)
                pltlabel_d = mass.npfit(calM_d)
                mass.plot2(data, calM_u, pltlabel_u, calM_d, pltlabel_d, ticks, labels, legend, fig_p)
                print("{:<8}{:<8}{:<8}{:<8}{:<8}{:<8}".format("e_x","e_y","h1_x","h1_y","h2_x","h2_y"))
                for i in pltlabel_u:
                    if isinstance(i, float):
                        print("{:<8.3f}".format(i), end='')
                    else:
                        print("{:<8s}".format('-'), end='')
                print()
                for i in pltlabel_d:
                    if isinstance(i, float):
                        print("{:<8.3f}".format(i), end='')
                    else:
                        print("{:<8s}".format('-'), end='')
                print()
            else:
                print("ERROR: Input file mismatch.")
        else:
            print("ERROR: BAND_GAP file does not exist.")
# plot Projected Band Structure
    elif args.projected:
        if not fig_p.vertical:
            fig_p.vertical = [-5.0, 5.0]
        bandfile = [f for i in ['PBAND_*.dat'] for f in glob.glob(i)] if len(args.input) == 1 and args.input[0] == 'BAND.dat' \
                    else [f for i in args.input for f in glob.glob(i)]
        if bandfile:
            from bandplot import projected
            darr, dbands, composition, s_elements = projected.bands(bandfile)
            index_f, labels_elements = projected.select(s_elements, args.partial)
            if len(index_f) > 0:
                ispin = [0 if s_elements[i][0].endswith('_DW') else 1 for i, j in index_f]
                if not elements:
                    elements = labels_elements
                if all(x == ispin[0] for x in ispin):
                    projected.pplot(darr, dbands, composition, ticks, labels, index_f, elements, legend, fig_p)
                else:
                    projected.pplot2(darr, dbands, composition, ticks, labels, index_f, elements, ispin, legend, fig_p)
            else:
                print("ERROR: Input mismatch.")
# plot Band Structure
    else:
        bandfile = [f for i in args.input for f in glob.glob(i)]
        len_bandfile = len(bandfile)
        if len_bandfile == 1:
            if not fig_p.vertical:
                fig_p.vertical = [-5.0, 5.0]
            arr, bands, ispin = readdata.bands(bandfile[0])
            if not dosfiles:
                if ispin == "Noneispin":
                    plots.Noneispin(arr, bands, ticks, labels, legend, fig_p)
                elif ispin == "Ispin" and not args.divided:
                    plots.Ispin(arr, bands, ticks, labels, legend, fig_p)
                elif ispin == "Ispin" and args.divided:
                    plots.Dispin(arr, bands, ticks, labels, legend, fig_p)
            else:
                darr, dele, s_elements = readdata.dos(args.dos)
                index_f, labels_elements = readdata.select(s_elements, args.partial)
                if not elements:
                    elements = labels_elements
                if ispin == "Noneispin":
                    plots.NoneispinWd(arr, bands, ticks, labels, darr, dele, index_f, elements, legend, fig_p)
                elif ispin == "Ispin" and not args.divided:
                    plots.IspinWd(arr, bands, ticks, labels, darr, dele, index_f, elements, legend, fig_p)
                elif ispin == "Ispin" and args.divided:
                    plots.DispinWd(arr, bands, ticks, labels, darr, dele, index_f, elements, legend, fig_p)
# plot DOS
        elif len_bandfile == 0:
            if dosfiles:
                if fig_p.output == "BAND.png":
                    fig_p.output = "DOS.png"
                darr, dele, s_elements = readdata.dos(dosfiles)
                index_f, labels_elements = readdata.select(s_elements, args.partial)
                if not elements:
                    elements = labels_elements
                plots.pdosfiles(darr, dele, index_f, elements, legend, fig_p)
            else:
                print("ERROR: No *.dat file.")
# compare two Band Structures
        elif len_bandfile == 2:
            if not fig_p.vertical:
                fig_p.vertical = [-5.0, 5.0]
            arr =   [''] * 2
            bands = [''] * 2
            ispin = [''] * 2
            arr[0], bands[0], ispin[0] = readdata.bands(bandfile[0])
            arr[1], bands[1], ispin[1] = readdata.bands(bandfile[1])
            if len(legend) < 3:
                legend = legend + [''] * (3 - len(legend))

            if all(x == "Noneispin" for x in ispin):
                plots.Noneispin2(arr, bands, ticks, labels, legend, fig_p)
            elif all(x == "Ispin" for x in ispin):
                plots.Dispin2(arr, bands, ticks, labels, legend, fig_p)
# compare three Band Structures
        elif len_bandfile == 3:
            if not fig_p.vertical:
                fig_p.vertical = [-5.0, 5.0]
            arr =   [''] * 3
            bands = [''] * 3
            ispin = [''] * 3
            arr[0], bands[0], ispin[0] = readdata.bands(bandfile[0])
            arr[1], bands[1], ispin[1] = readdata.bands(bandfile[1])
            arr[2], bands[2], ispin[2] = readdata.bands(bandfile[2])
            if len(legend) < 4:
                legend = legend + [''] * (4 - len(legend))

            if all(x == "Noneispin" for x in ispin):
                plots.Noneispin3(arr, bands, ticks, labels, legend, fig_p)
            elif all(x == "Ispin" for x in ispin):
                plots.Dispin3(arr, bands, ticks, labels, legend, fig_p)
        else:
            print("Input file mismatch.")

# bandplot
def pmain():
    parser = argparse.ArgumentParser(description='Plot the phonon band structure or DOS from phonopy results.',
                                     epilog='''
Example:
pbandplot -i BAND.dat -o BAND.png -l g m k g -d projected_dos.dat -g \$\\pi^2_4\$ -e Si C O
''',
    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', "--version",    action="version",     version="bandplot "+__version__+" from "+os.path.dirname(__file__)+' (python'+platform.python_version()+')')
    parser.add_argument('-s', "--size",       type=float, nargs=2,  help='figure size: width, height', metavar=('width','height'))
    parser.add_argument('-b', "--broken",     type=float, nargs=2,  help='broken axis: start, end')
    parser.add_argument('-H', "--hratios",    type=float,           help='height ratio for broken axis, default: 0.2', default=0.2)
    parser.add_argument('-y', "--vertical",   type=float, nargs=2,  help="frequency (THz) range", metavar=('start','end'))
    parser.add_argument('-g', "--legend",     type=str,             nargs='+', help="legend labels", default=[])
    parser.add_argument('-a', "--location",   type=str.lower,       nargs='+', help="arrange the legend location, default: best", default=[], metavar="str")
    parser.add_argument('-c', "--color",      type=str,             nargs='+', help="line color: b, blue; g, green; r, red; c, cyan; m, magenta; y, yellow;"+
                                                                                    "k, black; w, white", default=[], metavar="color")
    parser.add_argument('-k', "--linestyle",  type=str,             nargs='+', help="linestyle: solid, dashed, dashdot, dotted or tuple; default: solid",
                                                                                    default=[], metavar="str")
    parser.add_argument('-w', "--linewidth",  type=str,             nargs='+', help="linewidth, default: 0.8", default=[], metavar="0.8")
    parser.add_argument('-i', "--input",      type=str,             nargs='+', help="plot figure from .dat file, default: BAND.dat", default=["BAND.dat"])
    parser.add_argument('-o', "--output",     type=str,             help="plot figure filename, default: BAND.png", default="BAND.png")
    parser.add_argument('-q', "--dpi",        type=int,             help="dpi of the figure, default: 500", default=500)
    parser.add_argument('-j', "--bandconf",   type=str,             help="filename of band setting file, default: band.conf", default="band.conf")
    parser.add_argument('-l', "--labels",     type=str.upper,       nargs='+', default=[], help='labels for high-symmetry points, such as X S Y K M')
    parser.add_argument('-d', "--dos",        type=str,             nargs='?', default='', help="plot Phonon DOS from .dat file")
    parser.add_argument('-x', "--horizontal", type=float, nargs=2,  help="Phonon density of states range", metavar=('start','end'))
    parser.add_argument('-n', "--exchange",   action='store_true',  help="exchange the x and y axes of Phonon DOS")
    parser.add_argument('-e', "--elements",   type=str,             nargs='+', default=[], help="PDOS labels")
    parser.add_argument('-W', "--wratios",    type=float,           help='width ratio for DOS subplot, default 0.5', default=0.5)
    parser.add_argument('-z', "--fill",       type=float,           nargs='?', help='fill a shaded region between PDOS and axis, default: 0.2', default=None,
                                                                                    const=0.2, metavar="alpha")
    parser.add_argument('-f', "--font",       type=str,             help="font to use", default='STIXGeneral')

    args = parser.parse_args()

    labels = [re.sub("'|‘|’", '′', re.sub('"|“|”', '″', re.sub('^GA[A-Z]+$|^G$', 'Γ', i))) for i in args.labels]
    elements = [re.sub("'|‘|’", '′', re.sub('"|“|”', '″', i)) for i in args.elements]
    if args.dos != '':
        dosfile = args.dos or ('projected_dos.dat' if os.path.exists('projected_dos.dat') else '') or ('total_dos.dat' if os.path.exists('total_dos.dat') else '')
        dosfile = dosfile if os.path.exists(dosfile) else None
    else:
        dosfile = None

    color = []
    for i in args.color:
        j = i.split('*')
        if len(j) == 2:
            color += [ast.literal_eval(j[0])] * int(j[1]) if '(' in j[0] and ')' in j[0] else [j[0]] * int(j[1])
        else:
            color += [ast.literal_eval(i)] if '(' in i and ')' in i else [i]

    linestyle = []
    for i in args.linestyle:
        j = i.split('*')
        if len(j) == 2:
            linestyle += [ast.literal_eval(j[0])] * int(j[1]) if '(' in j[0] and ')' in j[0] else [j[0]] * int(j[1])
        else:
            linestyle += [ast.literal_eval(i)] if '(' in i and ')' in i else [i]

    linewidth = []
    for i in args.linewidth:
        j = i.split('*')
        linewidth += [float(j[0])] * int(j[1]) if len(j) == 2 else [float(i)]

    plt.rcParams['font.family'] = '%s'%args.font
    pltname = os.path.split(os.getcwd())[-1]
    s_ele = []
    formula = ''
    if os.path.exists('POSCAR-unitcell'):
        symbol, factor = readdata.symbols('POSCAR-unitcell')
        for i in range(len(symbol)):
            if factor[i] > 1:
                s_ele = s_ele + [symbol[i]] * factor[i]
                formula = formula + symbol[i]
                for j in str(factor[i]):
                    formula = formula + '$_'+ j + '$'
            else:
                s_ele = s_ele + [symbol[i]]
                formula = formula + symbol[i]

    if not elements and s_ele:
        elements = s_ele

    legend = args.legend or [formula] or [pltname]

    klabels = []
    if os.path.exists(args.bandconf):
        klabels = readdata.bandset(args.bandconf)
    if len(labels) == 0:
        labels=[re.sub('^GA[A-Z]+$|^G$', 'Γ', i) for i in klabels]

    broken = args.broken
    height_ratio = args.hratios if 0 < args.hratios < 1 else 0.2
    width_ratios = args.wratios if 0 < args.wratios < 1 else 0.5
    location = [int(i) if i.isdigit() else i for i in args.location]

    fig_p = cla_fig(output=args.output, size=args.size, vertical=args.vertical, horizontal=args.horizontal,
                    color=color, linestyle=linestyle, linewidth=linewidth, location=location, dpi=args.dpi,
                    height_ratio=height_ratio, width_ratios=width_ratios, exchange=args.exchange, fill=args.fill)
# plot Phonon Band Structure
    bandfile = [f for i in args.input for f in glob.glob(i)]
    len_bandfile = len(bandfile)
    if len_bandfile == 1:
        arr, fre, ticks = readdata.pbands(bandfile[0])
        if len(ticks) > len(labels):
            labels += [''] * (len(ticks) - len(labels))
        elif len(ticks) < len(labels):
            labels = labels[:len(ticks)]
        if dosfile:
            darr, dele = readdata.pdos(dosfile)
            if args.broken is None:
                pplots.NobrokenWd(arr, fre, ticks, labels, darr, dele, elements, legend, fig_p)
            else:
                pplots.BrokenWd(arr, fre, ticks, labels, broken, darr, dele, elements, legend, fig_p)
        else:
            if args.broken is None:
                pplots.Nobroken(arr, fre, ticks, labels, legend, fig_p)
            else:
                pplots.Broken(arr, fre, ticks, labels, broken, legend, fig_p)
# plot Phonon DOS
    elif len_bandfile == 0:
        if dosfile:
            if fig_p.output == "BAND.png":
                    fig_p.output = "DOS.png"
            darr, dele = readdata.pdos(dosfile)
            pplots.pdosfile(darr, dele, elements, legend, fig_p)
        else:
            print('No *.dat file.')
# compare two Phonon Band Structures
    elif len_bandfile == 2:
        arr = [''] * 2
        fre = [''] * 2
        ticks = [''] * 2
        arr[0], fre[0], ticks[0] = readdata.pbands(bandfile[0])
        arr[1], fre[1], ticks[1] = readdata.pbands(bandfile[1])
        if len(ticks[0]) > len(labels):
            labels += [''] * (len(ticks[0]) - len(labels))
        elif len(ticks[0]) < len(labels):
            labels = labels[:len(ticks[0])]
        if len(legend) < 3:
            legend += [''] * (3 - len(legend))

        if args.broken is None:
            pplots.Nobroken2(arr, fre, ticks[0], labels, legend, fig_p)
        else:
            pplots.Broken2(arr, fre, ticks[0], labels, broken, legend, fig_p)
# compare three Phonon Band Structures
    elif len_bandfile == 3:
        arr = [''] * 3
        fre = [''] * 3
        ticks = [''] * 3
        arr[0], fre[0], ticks[0] = readdata.pbands(bandfile[0])
        arr[1], fre[1], ticks[1] = readdata.pbands(bandfile[1])
        arr[2], fre[2], ticks[2] = readdata.pbands(bandfile[2])
        if len(ticks[0]) > len(labels):
            labels += [''] * (len(ticks[0]) - len(labels))
        elif len(ticks[0]) < len(labels):
            labels = labels[:len(ticks[0])]
        if len(legend) < 4:
            legend += [''] * (4 - len(legend))

        if args.broken is None:
            pplots.Nobroken3(arr, fre, ticks[0], labels, legend, fig_p)
        else:
            pplots.Broken3(arr, fre, ticks[0], labels, broken, legend, fig_p)
    else:
        print("Input file mismatch.")

