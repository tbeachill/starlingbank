![PyPI](https://img.shields.io/pypi/v/starlingbank.svg)

# starlingbank

An **unofficial** python package that provides access to parts of the Starling bank API. Designed to be used for personal use (i.e. using personal access tokens).

- [starlingbank](#starlingbank)
  - [Change Log](#change-log)
  - [Links](#links)
  - [Installation](#installation)
  - [Usage](#usage)
    - [API Key Scope Requirements](#api-key-scope-requirements)
    - [Import](#import)
    - [Initialisation](#initialisation)
    - [Data](#data)
      - [Basic Account Data](#basic-account-data)
      - [Balance Data](#balance-data)
    - [Spaces](#spaces)
      - [Update a Space](#update-a-space)
      - [Download a Space Image](#download-a-space-image)
      - [Saving Spaces](#saving-spaces)
        - [Add to / withdraw from a Saving Space](#add-to--withdraw-from-a-saving-space)
      - [Spending Spaces](#spending-spaces)


## Change Log
18/12/2019
* Removed `available_to_spend` property as this is no longer supported by the API.

23/02/2018
* Updated to use v2 API.
* `currency` is no longer a property of the balance data.
* `id` and `name` are no longer properties of the account data.
* `account_number` is now `account_identifier`.
* `sort_code` is now `bank_identifier`.
* An API call is now made when initialising a StarlingAccount instance, even with `update=False`. This is to get the minimum data needed to start working with an account.

## Links

* https://www.starlingbank.com/
* https://developer.starlingbank.com/

## Installation
```shell
pip install starlingbank
```

## Usage
### API Key Scope Requirements
To use all of the functionality this package affords, the following API scopes are required:

* account:read
* account-identifier:read
* balance:read
* savings-goal:read
* savings-goal-transfer:read
* savings-goal-transfer:create
* space:read

### Import
```python
from starlingbank import StarlingAccount
```

### Initialisation
```python
my_account = StarlingAccount("<INSERT API TOKEN HERE>")
```
If using a sandbox token:
```python
my_account = StarlingAccount("<INSERT API TOKEN HERE>", sandbox=True)
```
By default, to save on wasted API calls only minimal data is collected when you initialise a StarlingAccount. To optionally update all data on initialisation use the following:
```python
my_account = StarlingAccount("<INSERT API TOKEN HERE>", update=True)
```

### Data
4 data sets are currently supported:

1. Basic Account Data
2. Balance Data
3. Saving Space Data
4. Spending Space Data

 You have to request / refresh each set of data as required with the following commands:

```python
my_account.update_account_data()
my_account.update_balance_data()
my_account.update_spaces()
```

#### Basic Account Data
Properties:

* account_identifier
* bank_identifier
* currency
* iban
* bic
* created_at

Example:
```python
print(my_account.account_identifier)
```

#### Balance Data
Properties:

* cleared_balance
* effective_balance
* pending_transactions
* accepted_overdraft

Example:

```python
print(my_account.effective_balance)
```

### Spaces
Saving Spaces and Spending Spaces are stored as a dictionary of objects where the dictionary key is the Space uid. The methods in this section can be used on either type of Space, just replace `saving_spaces` with `spending_spaces`.

To get a list of Space names and their respective uids you can run:
```python
for uid, space in my_account.saving_spaces.items():
    print("{0} = {1}".format(uid, space.name))
```

_Note: Values are in minor units e.g. £1.50 will be represented as 150._

Example:
```python
print(my_account.saving_spaces['c8553fd8-8260-65a6-885a-e0cb45691512'].total_saved_minor_units)
```

#### Update a Space
The `update_spaces_data()` method will update all Spaces but you can also update them individually with the following method:
```python
my_account.saving_spaces['c8553fd8-8260-65a6-885a-e0cb45691512'].update()
```

#### Download a Space Image
You can download the image associated with a Space to file with the following method:
```python
my_account.saving_spaces['c8553fd8-8260-65a6-885a-e0cb45691512'].get_image('<YOUR CHOSEN FILENAME>.png')
```
_Note: If the filename is ommitted the name of the Space will be used. You can optionally specify a full path alongside the filename if required._

#### Saving Spaces
Each Saving Space has the following properties:
* uid
* name
* target_currency
* target_minor_units
* total_saved_currency
* total_saved_minor_units
* saved_percentage
* sort_order
* state

##### Add to / withdraw from a Saving Space
You can add funds to a Saving Space with the following method:
```python
my_account.saving_spaces['c8553fd8-8260-65a6-885a-e0cb45691512'].deposit(1000)
```

You can withdraw funds from a Saving Space with the following method:
```python
my_account.saving_spaces['c8553fd8-8260-65a6-885a-e0cb45691512'].withdraw(1000)
```

_Note: Both methods above will call an update after the transfer so that the local total_saved value is correct._

#### Spending Spaces
Each Spending Space has the following properties:
* uid
* name
* balance_currency
* balance_minor_units
* card_association_uid
* sort_order
* spending_space_type
* state
