# Lab Utilities
Lab Utilities provides general-purpose code that can help with an automated lab

## Installation

To install, run the following from the command line: </br>
`git clone https://github.com/stefangolas/lab_utilities.git` </br>
`cd lab_utilities` </br>
`pip install -e .` </br>

Use `set-lab-email` to configure the built-in email service

## Resources

Documentation for the importable resources provided by this library. All of these are available in the package namespace.

### ConfigLoader

The `ConfigLoader` class creates equipment interfaces defined in config.json. This enables a separation of distributed, version-controlled code from local equipment configurations.

**config.json**
```json
{"equipment":
        "pump": {
            "type": "path",
            "import": "C:\\Users\\user\\modular_lab\\equipment\\pumps\\agrow_pumps",
            "class": "DualArray",
            "args": {}
         }
 }

```

```python
configuration = ConfigLoader('config.json')
pump_int = configuration.load_class('pump', simulating = simulating)
```

We can apply arguments such as `simulating` at run-time to create the interface. 

### ExperimentalDataHandler

The `ExperimentalDataHandler` class creates a unique directory for storing data (including logs, instrument data, and input parameters) from an experiment.

### email_error
The function `email_error` very simply uses a gmail service to send emails from Python.

To use this function you must create a gmail account with an App Password [according to this guide](https://towardsdatascience.com/how-to-easily-automate-emails-with-python-8b476045c151)

Then, apply the account information to these environment variables: `lab_utilities_email` and `lab_utilities_email_password`.

```python
email_addresses = ['example@123.com']
email_error(recipients = email_addresses, subject = 'Robot Error', error='Exception Raised')
```



