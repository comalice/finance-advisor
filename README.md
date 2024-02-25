# Using `portfolio`

# Abstractions

## Transaction

A transaction is composed of a date, a security, a quantity, and price. It is the fundamental unit of a collection.

## Collection

A collection is composed of transactions.

## Position

A position is made up of a group of transactions for a single security. Calculating cost basis, market value, and 
gain/loss is done at the position level and is configurable.

## Portfolio

A portfolio is a filtered view of positions within one or more collection. The filters can be based on any data point
contained in a position.