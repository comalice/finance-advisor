# Using `portfolio`

# Abstractions

## Transaction

A transaction is composed of a date, an action, a security, a quantity, and price. It is the fundamental unit of a collection.

## Ledger Entry

A ledger entry is composed of two or more transactions whose values sum to 0.

They follow `ledger-cli` formatting rules and look something like this:

```ledger-cli
2029-01-25 * Buy AAPL
    Assets:Investments:Stocks:AAPL  100 AAPL
    Assets:Investments:Cash  $-1000
```

If this were CSV entries, we would need two lines, one for the credit and one for the debit. It would look something like this:

```csv
Ticker,Date,Action,Quantity,Price,Account,Amount
AAPL,2029-01-25,Buy,100,,Assets:Investments:Stocks:AAPL,1000
AAPL,2029-01-25,Buy,100,,Assets:Investments:Cash,-1000
```

Here the exchange rate is implied and the credit/debits are explicit. We could also write something like:

```ledger-cli
2029-01-25 * Buy AAPL
    Assets:Investments:Stocks:AAPL  100 AAPL @ $10
    Assets:Investments:Cash
```

Again, if this were CSV entries. It looks like this:

```csv
Ticker,Date,Action,Quantity,Price,Account,Amount
AAPL,2029-01-25,Buy,100,10,Assets:Investments:Stocks:AAPL,
AAPL,2029-01-25,Debit,,,Assets:Investments:Cash,-1000
```

That is, we are credited 100 AAPL security at a price of $10 each, and our cash account is debited $1000.

    But why have two kinds of transaction collection? We have ledger entries and this "collection"?

## Collection

A collection is composed of transactions.

## Position

A position is made up of a group of transactions for a single security. Calculating cost basis, market value, and 
gain/loss is done at the position level and is configurable.

## Portfolio

A portfolio is a filtered view of positions within one or more collection. The filters can be based on any data point
contained in a position.
# Data Flow

Data flows from sources, is munged together in "positions", is filtered into "portfolios", and is then used to produce reports.

```
                                                                                               
                                                                                               
                                                                     ┌─────────────────────┐   
                                                                     │         CCXT        │   
                                                                     │                     │   
                                                                     │                     │   
  ┌───────────────┐ ┌─────────────────────┐         ┌──────────────┐ │                     │   
  │     .CSV      │ │     .ledger         │         │    Yahoo     │ │  Kraken       etc.  │   
  └───────────────┘ └─────────────────────┘         └──────────────┘ └─────────────────────┘   
                                                                                               
  ┌───────────────────────────────────────┐         ┌──────────────────────────────────────┐   
  │                                       │         │                                      │   
  │  Portfolio Sources (IPortfolioSource) │         │   Market Data Sources (IDataSource)  │   
  │                                       │         │                                      │   
  └──────────────────┬────────────────────┘         └──────────────────┬───────────────────┘   
                     │                                                 │                       
                     │                                                 │                       
                     └─────────────────┐                               │                       
                                       │                               │                       
                                       ▼                               │                       
                             ┌─────Positions──────┐                    │                       
                             │                    │                    │                       
                             │ - market data ◄────┼────────────────────┘                       
                             │                    │                                            
                             │ - transaction data │                                            
                             │                    │                                            
                             └─────────┬──────────┘                                            
                                       │                                                       
                                       │                                                       
                                       │                                                       
                                       │                                                       
                                       │                                                       
                                       │                                                       
                                       ▼                                                       
                                ┌────────────┐                                                 
                                │  Portfolio │                                                 
                                └──────┬─────┘                                                 
                                       │                                                       
                                       │                                                       
                                       │                                                       
                                       │                                                       
                                       │                                                       
                                       │                                                       
                                       │                                                       
                                       ▼                                                       
                                ┌────────────┐                                                 
                                │  Reporting │                                                 
                                └────────────┘                                                 
                                                                                               
                                                                                               
```

# TODO - Make some provision for custom analysis. Maybe middleware or plugins?

Middleware might work well. We would have some sort of processing pipeline that we could allow others to plug into. Flask has something that looks like this (from [here](https://stackoverflow.com/a/68748517/7823006)):

```python
@app.before_request
def gather_request_data():
    g.method = request.method
    g.url = request.url

@app.after_request
def log_details(response: Response):
    g.status = response.status

    logger.info(f'method: {g.method}\n url: {g.url}\n status: {g.status}')

    return response
```

And that is pretty fantastic. This would allow us to expose interfaces for any part of our data processing pipeline.

Let's look at the basic flow of data one more time:

```
data on disk --> read data --> munge data --> pass data to repository --> filter data --> produce reports 
```

The "filter data" step is where the basic reporting happens. If we add hooks in all the obvious places (between every major step), we'd have the following list of hooks:

- after reading data
- after munging data
- after passing data to repository
- after basic data filtering (produces positions and opens up access to views of positions)
- after producing reports

Obviously, each would have two aliases, one for before and one for after. For example "after munging data" would also be "before passing data to repository".

If a user needs to pass data between middleware steps (not just the expect IO), we would require the registration of one or more service that subsequent middleware could access.

# TODO - Figure out underlying data schema.

A dataframe wrapped with class accessors might work. Something like a services architecture from C#, where we have a service that manages the in-memory representation of our information (backed by whatever, so it would be the `IRepository` offered as a service). Then middleware would be able to grab the singleton IRepository service and pull information and push updates as necessary.

This would alter the current data flow to be something like

```
on disk (csv, legder) --> some kind of file specific reader that produces a dataframe --> a munger to combine multiple data sources --> pass the dataframe to the repository service
```