# MITRE DASH-board🏄🏽‍♂️

Update the MiTRE dashboard provided by [HELK](https://github.com/Cyb3rWard0g/HELK).

## TLDR

> This package loads the most recent data from the [MITRE ATT&CK®](https://attack.mitre.org/) framework and and converts it to parsable csv files.

> In a second step the data can be parsed by [logstash](https://www.elastic.co/logstash) and imported into your [elasticsearch](https://www.elastic.co/elasticsearch/) instance.
This step should be repeated in an interval of 3 month to keep your [CTI](https://en.wikipedia.org/wiki/Threat_intelligence) up to date!

> Additionally, you can upload the metadata of the [HELK](https://github.com/Cyb3rWard0g/HELK) dashboard to your Kibana endpoint. This step is necessary only once and if the dashboard wasn't imported previously.


![helkDashAll](https://github.com/3lLobo/mitre-dash/assets/25290565/3b996dd7-5af9-4855-92cd-4a91bad27027)
![helkDashApt](https://github.com/3lLobo/mitre-dash/assets/25290565/cd4c0739-7dac-417f-a8ee-a5d55881486e)


## Usage

### Package installation

```bash
pip install mitre-dash
```

### Get and process the latest Mitre data

```bash
attack_fetch
```

Optional flags:
- `--matrix_name` to specify the matrix. Options are `enterprise-attack`, `mobile-attack` and `ics-attack`.
- `--include_subtechniques` to include sub_techniques. This will result in a factor 10 increase in data size (20GB).
- `--include_detection` to include detection methods. This is very verbose, will increase log size and might break logstash parsing due to special characters.
- `--include_descriptions` to include descriptions of techniques, software, groups, etc. Same as above ⬆️.
- `--output_dir` to specify the output directory. Default is `./output`.
- `--help` or `-h` to get help.

### Import dashboard to Kibana

In total you will import:
- 1 index pattern
- 2 dashboards
- a bunch of custom visualizations

Run:
```bash
attack_dash_up
```
Next you will be prompted to enter your Kibana host-address and credentials.
We use the same script as the [HELK](https://github.com/Cyb3rWard0g/HELK) to import the metadata.

> ⚠️ This step is only necessary once and if the dashboard wasn't imported previously!!!

### Parse data with logstash

Now upload the new data to your elasticsearch instance:
```bash
attack_parse
```
Next you will be prompted to enter your elasticsearch host-address and credentials.

This will create a 'logstash' folder in your current directory with:
- `logstash.conf` to parse the csv data.
- `docker-compose.yml` to run logstash as a contained service.
- `.env` to facilitate the provided credentials.

Finally two parallel processes will be started:
- `docker-compose up` to run logstash.
- `nc <logstash-host> 32173 -q 11 < output/<attack-matrix>.csv` to send the data to logstash.

The second process is repeated for every attack matrix csv file in the output folder.

> ⚠️ Prepare for a long ride. Get some popcorn while 13M logs are ingested 🍿


<!-- ## Old

Update Mitre Dashboard

> Goal: Update the Mitre Dashboard from the [HELK](https://github.com/Cyb3rWard0g/HELK) with the latest data.

### Challenge

- [x] The [old data](https://raw.githubusercontent.com/Cyb3rWard0g/HELK/master/docker/helk-logstash/enrichments/cti/mitre_attack.csv) does not match with newer data, both in column names and count.
- [ ] Different sources with varying data formats.
- [ ] Sub-techniques not included in the old data. 

<!-- ## Mitre script

> Mitre provides python scripts to parse the data as csv.

The script is in the [allCsv]{./allCsv} folder together with the pulled csv files.
With a tad of column renaming and 2 table joins the resulting csv looks a lot like the original table.
We miss the `data_source` or `log_source` intel. --> 

