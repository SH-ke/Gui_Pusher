from GuiPusher import GuiPusher
from argparse import ArgumentParser


def main():
    gp = GuiPusher()
    if args.getlike:
        gp.get_likes()
    if args.isalive:
        gp.is_alive()
    if args.guitime:
        gp.get_gui_time()
    if args.csv:
        gp.load_by_csv(args.csv)
    if args.on:
        gp.loop_monitor()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--getlike",
        action="store_true",
        help="get the shop names you care about",
        default=False,
    )
    parser.add_argument(
        "--isalive",
        action="store_true",
        help="confirme if Gui_Pusher is alive",
        default=False,
    )
    parser.add_argument(
        "--guitime",
        action="store_true",
        help="get the last regular init of Gui_Pusher",
        default=False,
    )
    parser.add_argument("--csv", type=str, help="load data to usr.dat by csv file")
    parser.add_argument(
        "--on", action="store_true", help="trun on Gui_Pusher", default=False
    )
    args = parser.parse_args()
    main()
