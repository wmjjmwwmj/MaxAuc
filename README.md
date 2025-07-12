# MaxAuc: A Max-Plus-Based Auction Approach for Multi-Robot Allocations for Time-Ordered Temporal Logic Tasks

🎉 **This paper has been accepted by IEEE IROS 2025!**

## Paper Overview

This project implements the multi-robot task allocation algorithm proposed in the paper *MaxAuc: A Max-Plus-Based Auction Approach for Multi-Robot Allocations for Time-Ordered Temporal Logic Tasks*. In this study, we introduce a novel approach, MaxAuc, which integrates Auction-based task allocation with Max-Plus algebra to handle time constraints. Unlike existing methods, MaxAuc approximates task priorities using Max-Plus computations in the auction, avoiding the explicit solution of constraint optimization problems. Our experimental results demonstrate that MaxAuc is highly scalable with respect to both the number of robots and tasks while maintaining a reasonable performance trade-off compared to the baseline's optimal but exhaustive solution.

## Branches

This project contains two main branches:

1. **Baseline**: This branch implements the baseline algorithm, which uses a traditional auction-based task allocation approach, serving as a performance baseline.
2. **MaxAuc**: This branch implements the MaxAuc algorithm, which combines Max-Plus algebra with auction-based task allocation for scalable multi-robot task assignment. Experiments of greedy algrithm is also conducted by this branch, where task priorities are set to zero.

## Case Study

![Watch the demo](https://img.youtube.com/vi/w_kYA31kLRc/0.jpg)

[Click here to watch the demo on YouTube](https://www.youtube.com/watch?v=w_kYA31kLRc)

## Contributing

Contributions are welcome! Please submit pull requests to improve the code or add new features. For more information on contributing, please refer to `CONTRIBUTING.md`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
