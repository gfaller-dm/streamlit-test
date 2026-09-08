CREATE OR REPLACE TABLE workspace.default.sports_federations_safeguarding_country (
	Federation STRING, --DFB
	Sport STRING, --Football
	Country STRING, --Germany
	CodeofEthics STRING, --Y/N
	CodeofConduct STRING, --Y/N
	SpecialEntityDedicated STRING --Y/N
)
USING DELTA;
