from pathlib import Path
import pandas as pd
import click

from DataSources import yahoo
from DataSources.yahoo import Yahoo
from PortfolioSources.csv import CsvPortfolioSource
from Report import basic
from portfolio import Portfolio


@click.command()
@click.option('--file', type=click.Path(exists=True), prompt='Enter file path:')
def main(file):
    """CLI interface for portfolio analysis."""
    # Check file extension using pathlib, if 'ledger' is in extension then process as ledger, else process as a 'csv'.
    file_path = Path(file)
    portfolio_source = None

    # Ingest data from file
    if file_path.suffix == '.ledger':
        raise NotImplementedError("Ledger file processing not implemented.")
    elif file_path.suffix == '.csv':
        portfolio_source = CsvPortfolioSource(file_path)
        print("Processing csv file...")
    else:
        print("File type not supported.")
        return 1

    # Spin up source contexts. We can do multiple sources in this line like so:
    # with CsvPortfolio(file_path) as csv, LedgerPortfolio() as yahoo:
    # TODO add a way to handle N input files from arbitrary file types.
    with portfolio_source as _portfolio_source:
        _data_source = Yahoo()

        # Init portfolio
        portfolio = Portfolio(data_sources=[_data_source], positions=_portfolio_source.positions)

        portfolio.get_latest_prices()

        print(f"Portfolio Value: ${portfolio.get_value():.2f}")
        print(f"Cost Basis: ${portfolio.cost_basis():.2f}")
        print(f"Gain/Loss: ${portfolio.gain_loss():.2f}, ({portfolio.gain_loss_percent()*100:.4f}%)")
        print(f"Average Time Held: {portfolio.average_time_held()}")
        print(f"ARR: {portfolio.get_annualized_return()*100:.4f}%")

        # Same as above, but for each position.
        for ticker, position in portfolio.positions.items():
            print(f"{ticker}, status: {position.status}")
            print(f"\tValue: ${position.get_value():.2f}")
            print(f"\tQuantity: {position.get_quantity()}")
            print(f"\tCost Basis: ${position.get_cost_basis():.2f}")
            print(f"\tTotal Time Held: {position.get_time_held()}")
            print(f"\tPercent Return: {position.get_return_percent()*100:.4f}%")
            print(f"\tARR: {position.get_annualized_return()*100:.4f}%")


if __name__ == "__main__":
    main()
