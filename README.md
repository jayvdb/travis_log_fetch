# travis_log_fetch
## A command line tool to fetch logs from Travis-CI.

```
$ travis_log_fetch --help
usage: travis_log_fetch [options] [target [target2 ...]]

travis_log_fetch fetches many log files. Args that start with '--' (eg. -d)
can also be set in a config file (~/.travisrc or .travisrc or specified via
-c). The recognized syntax for setting (key, value) pairs is based on the INI
and YAML formats (e.g. key=value or foo=TRUE). For full documentation of the
differences from the standards please refer to the ConfigArgParse
documentation. If an arg is specified in more than one place, then commandline
values override environment variables which override config file values which
override defaults.

positional arguments:
  targets               targets

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        config file path
  -d DIR, --dir DIR     log storage directory
  --access-token ACCESS_TOKEN
                        Github access token [env var: GITHUB_ACCESS_TOKEN]
  -v, --verbose         verbose
  -r, --refresh         refresh
  --forks               fetch forks
  -f, --force           force
  --format FORMAT       log filename format
  -a, --all             all
  -o, --old             old
  -s, --self            fetch own repos
  -w, --wait            wait for jobs to complete
  --sleep SLEEP         time to wait for jobs to complete
  --count COUNT         number of old logs to fetch
```

## Target identifiers

A target on the command line is parsed using [Target](https://github.com/jayvdb/travis_log_fetch/blob/master/travis_log_fetch/_target.py), and may be:

1. repository: `jayvdb/travis_log_fetch`
2. build id: `jayvdb/travis_log_fetch@90471372` which refers to  https://travis-ci.org/jayvdb/travis_log_fetch/builds/90471372
3. job id: `jayvdb/travis_log_fetch:90471373` which refers to https://travis-ci.org/jayvdb/travis_log_fetch/jobs/90471373
4. logical build number: `jayvdb/travis_log_fetch/23`
5. logical job number: `jayvdb/travis_log_fetch/23.2`
6. a Travis URL such as https://travis-ci.org/jayvdb/travis_log_fetch, https://travis-ci.org/jayvdb/travis_log_fetch/builds/90471372 or https://travis-ci.org/jayvdb/travis_log_fetch/jobs/90471373
