use phenx;

ALTER TABLE publications MODIFY COLUMN protocol_ids text;
ALTER TABLE publications MODIFY COLUMN disease_phenotype text;
ALTER TABLE publications MODIFY COLUMN primary_research_focus text;
ALTER TABLE publications MODIFY COLUMN funding_source text;
ALTER TABLE publications MODIFY COLUMN award_num text;
ALTER TABLE publications MODIFY COLUMN foa text;
