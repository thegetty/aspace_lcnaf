# LCNAF Bulk Import for ArchivesSpace

## Requirements
* Python version 3.7
* pipenv
* requests

## Installation

### pipenv
**--If you already have pipenv installed, skip this section--**
Pipenv automatically creates and manages a virtualenv for your projects, as well as adds/removes packages from your Pipfile as you install/uninstall packages (*Sources*: [pipenv](https://pipenv.readthedocs.io/en/latest/#)). Instruction for installing pipenv can be found [here](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv). 

### Requests package
* In command window, go to the cloned directory `/`
* Install requests with pipenv: `$ pipenv install requests`
	(*This will generate a pip file*)

## Instructions

### Set Login Info
* Open `loginInfo.py` 
* Add information accordingly, sandbox or production

### Retrieve all agents records by type
* In command window, navigate to the cloned directory `/`
* Execute this command: **`$ pipenv run python retrieve.py arg1 arg2`**
	* replace **`arg1`** with **sb** or **prod**
	* replace **`arg2`** with one of the following:
		* **person**
		* **corporate**
		* **family**
		* **software**

* The result is a CSV list of all agents by the input type, which is saved in either `/data/sb` or `/data/prod` depending on the input environment. It includes:
	* Aspace_ID - unique identifier in ASpace
	* Names - Display name in ASpace
	* Authority_ID : authority id if any
	* Source : source of name

### Reconciliation in OpenRefine
#### Download and install the reconciliation service
* Use this [Library of Congress Reconciliation Service for OpenRefine](https://github.com/mphilli/LoC-reconcile) written by Michael Phillips.
* Follow the instructions for installation and usage in OpenRefine

#### Reconcile
* Import the retrieved CSV list of agents to OpenRefine
* Before running the recon service, create a new column based on the **Names** column. Just leave it as is, no need for transformation. Move the new column to the end.
* Run the recon service on the new column.
* After the service is completed, check the matching. 
* [More information on reconciliation can be found here](https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation). 
*_Notes_: Some records could be already imported from LCNAF, especially those with source **naf**, and have authority id. However, as the reconciliation takes time to complete, it is best to run the services on all records and facet them afterward.*

#### Get uri
* If not all names can be matched, use [Facet](https://github.com/OpenRefine/OpenRefine/wiki/Faceting) to filter down to just the subset of rows that you want to change in bulk. 
* Click the arrow next to the same recon column, select `Edit Column > Add column based on this column…`
	* Enter new column name **uri**
	* In the “Expression” box, replace `value` with `(cell.recon.candidates[0].id).split('"')[0]` ; then OK
* Exclude any agents with existing Authority_ID that are the same as LCNAF ID. The API will return error if you attempt to create a new agent record witht he same uthority id.
* Export as Comma-separated value, which only contain selected faceted rows.
* Move the exported file to the folder **`aspace_lcnaf/data/sb`** or **`aspace_lcnaf/data/prod`**.

#### Create/import LCNAF records
* Make sure:
	* Reconciled/matched CSV file is located in either **`aspace_lcnaf/data/sb`** or **`aspace_lcnaf/data/prod`**.
	* LCNAF uri is the last column in the CSV.
* In command window, navigate to the cloned directory `/`
* To execute, use this command line: **`$ pipenv run python run.py arg1 arg2 arg3 arg4`**
	* replace **`arg1`** with **create**
	* replace **`arg2`** with **sb** or **prod**
	* replace **`arg3`** with **filename** of the reconciled CSV with lcnaf id, excluding the `.csv` extension
	* replace **`arg4`** with one of the following
		* **person**
		* **corporate**
		* **family**
		* **software**
	Example: `$ pipenv run python run.py create sb people_recon person`
* The result includes new ASpace Agent records with data from LCNAF, and edited csv file including the ASpace ID of the newly created records. This aims to facilitate the merge later as the existing id is mapped to the new id. The new csv file is name as `{your_recon_filename}_imported`, and in the same folder as your reconciled file **`aspace_lcnaf/data/sb`** or **`aspace_lcnaf/data/prod`**.
*__Notes__: 
	* You don't have to worry about possible duplicates/agents with same reconciled lcnaf id in the input CSV. The script has mechanism to prevent multiple creations of the same lcnaf.
	* ERROR: error might occur due to:
		* The MARC codes don't match to the right type of agents, meaning when reconcile a person agent, the services would return a match from a corporate authority file, and the script wouldn't parse the right tags.*

#### Merge agent records
* Make sure:
	* Existing ASpace ID is in the first column.
	* New ASpace ID is in the last column.
* In command window, navigate to the cloned directory `/`
* To execute, use this command line: **`$ pipenv run python run.py arg1 arg2 arg3 arg4`**
	* replace **`arg1`** with **merge**
	* replace **`arg2`** with **sb** or **prod**
	* replace **`arg3`** with **filename** of the CSV with new ASpace IDs, excluding the `.csv` extension
	* replace **`arg4`** with one of the following
		* **person**
		* **corporate**
		* **family**
		* **software**
	Example: `$ pipenv run python run.py merge sb people_recon_imported person`




