import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="...")

    parser.add_argument(
        "--settings_n",
        default="4.2.2",
        type=str,
        help="Choose the settings source.",
    )
    # parser.add_argument(
    #     "--update_options_interval",
    #     default=3,
    #     type=int,
    #     help="Choose the interval of options' benefit updating.",
    # )
    parser.add_argument(
        "--price_umax",
        default=1,
        type=float,
        help="Choose the maximum value of prince.",
    )
    parser.add_argument(
        "--price_alpha",
        default=1,
        type=float,
        help="Choose the rate of decay of reward.",
    )
    parser.add_argument(
        "--bid_bmax",
        default=1,
        type=float,
        help="Choose the max of bid value.",
    )
    parser.add_argument(
        "--bid_beta",
        default=1,
        type=float,
        help="Choose the amplification effect of the reward on the bid.",
    )
    parser.add_argument(
        "--bid_lambda",
        default=1,
        type=float,
        help="Choose the rate of decay of the cost.",
    )
    parser.add_argument(
        "--seed",
        default=42,
        type=int,
        help="Sample seed of main.",
    )
    parser.add_argument(
        "--sample_interval",
        default=0.2,
        type=float,
        help="Sample interval for robots",
    )
    parser.add_argument(
        "--sample_frequency",
        default=5,
        type=int,
        help="Sample frequency for robots",
    )
    parser.add_argument(
        "--assign_bid_num",
        default=1,
        type=int,
        help="Max bid count for auction to assign.",
    )

    args = parser.parse_args()
    # eval() 是一个内置函数，它将字符串中的表达式作为 Python 代码进行执行。在这行代码中，eval(args.step) 将对命令行传入的 step 参数进行求值。
    # args.step = eval(args.step)
    return args