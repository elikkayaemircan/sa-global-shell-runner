# SA Global Shell Runner

A top-level program to offer parallel execution and reporting for custom scripts on Server Automation Global Shell.

## Usage Examples

An example to use reporting utility.
```bash
[username@hostname sa-global-shell-runner] $ python main.py -r --run_for DNUSERNAME --threads 4 --action dry_run
Preparing enviroment for action dry_run on target Admin DNUSERNAME...
Number of device to run report 480! Starting...
Collecting report for dry_run on target Admin DNUSERNAME...
### RUN COMPLETED!
    A NICE QUOTE TO SAY GOODBYE.
```

An example to use configuration utility.
```bash
[username@hostname sa-global-shell-runner] $ python main.py -c --run_for DNUSERNAME -t 2 --action dry_run
Preparing enviroment for action dry_run on target Admin DNUSERNAME...
Number of device to configure 480! Starting...
Collecting configuration results for dry_run on target Admin DNUSERNAME...
### RUN COMPLETED!
    A NICE QUOTE TO SAY GOODBYE.
```

## Disclaimer

The code in this repository is developed by me as a side project. I use them in my company as well. The version that I use in my company differs from the one published here. All the information is unrelated with the one using inside.

I share them to show only my coding experience.
