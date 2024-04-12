# PolkaStakeSphere - Unlocking Valuable Insights from Polkadot's Blockchain

Welcome to PolkaStakeSphere, a pioneering project designed to uncover valuable stories and insights from the Polkadot ecosystem. Our goal is to empower blockchain enthusiasts, developers, and analysts with the tools they need to explore and understand the rich data landscape of Polkadot. 

**This repository is a work in progress, and we would like to express our gratitude to [DTC Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) for providing the scaffold to kick-start this project.**

## Portable Data Stack: Enabling Local Data Analytics

The core principle of PolkaStakeSphere is the "Portable Data Stack." We firmly believe that data analytics should be accessible to everyone, regardless of their resources or technical expertise. With this in mind, we have designed this repository to enable seamless data analytics on your local machine, eliminating the need for expensive cloud infrastructure.

PolkaStakeSphere allows you to set up your own local data warehouse and dive into the fascinating world of Web3 data without the burden of high costs or complex dependencies. Our carefully crafted tools and frameworks enable you to extract, transform, and analyze blockchain data right on your personal computer.

## Key Features

- **Polkadot Ecosystem Insights**: Leverage the raw big dataset collection from [substrate-etl](https://github.com/colorfulnotion/substrate-etl) for both Polkadot and Kusama networks (relay and parachain) to extract and analyze data. Gain valuable insights into staking, validator status, and more.

- **Local Data Warehouse**: PolkaStakeSphere empowers you to set up your own data analytics environment without relying on cloud services. This ensures privacy and gives you complete control over your data.

- **Zero Cloud Dependency**: Once the raw dataset is extracted to your local data warehouse, you can operate independently of cloud platforms. This eliminates ongoing costs and potential data privacy issues.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following:

- Follow the instructions from [substrate-etl, quick-start-analytics-hub](https://github.com/colorfulnotion/substrate-etl#quick-start-analytics-hub) to add raw datasets to your Google Cloud project.
- Populate [env.example](./env.example) with the appropriate configuration values.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/shamb0/pds-PolkaStakeSphere.git
   ```

2. Navigate to the cloned directory:
   ```bash
   cd pds-PolkaStakeSphere
   ```

3. Install the required Python libraries:
   - Follow the instructions directed by make commands:
     ```bash
     make prepare_environment
     source .activate_env && activate_env
     make install_dev_dependencies
     ```

4. Start a local deployment server of [Dagster](https://dagster.io) and materialize data assets in the pipeline:
   ```bash
   make run_dagster_dev
   ```

5. Visualize the streamlit insight dashboard:
   ```bash
   make view_leaderboard
   make view_validator_status
   ```

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

shamb0 - [@0shamb0](https://twitter.com/your_twitter) - r.raajey@gmail.com

Project Link: [https://github.com/shamb0/pds-PolkaStakeSphere](https://github.com/shamb0/pds-PolkaStakeSphere)

