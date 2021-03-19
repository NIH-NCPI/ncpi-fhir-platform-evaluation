import pytest

from fhireval.test_suite.capability_statement import get_resource, get_capability_statement

# Which bullet point do these tests map to
test_id = f"{'2.1.1':<10} - Resource Interaction"

# How much weight do we attribute to the tests in this file
test_weight = 2

@pytest.mark.capability_statement
# List of structures expected to be found
@pytest.mark.parametrize("resource", ['Account','ActivityDefinition','AdverseEvent','AllergyIntolerance','Appointment','AppointmentResponse','AuditEvent','Basic','Binary','BodySite','Bundle','CapabilityStatement','CarePlan','CareTeam','ChargeItem','Claim','ClaimResponse','ClinicalImpression','CodeSystem','Communication','CommunicationRequest','CompartmentDefinition','Composition','ConceptMap','Condition','Consent','Contract','Coverage','DataElement','DetectedIssue','Device','DeviceComponent','DeviceMetric','DeviceRequest','DeviceUseStatement','DiagnosticReport','DocumentManifest','DocumentReference','EligibilityRequest','EligibilityResponse','Encounter','Endpoint','EnrollmentRequest','EnrollmentResponse','EpisodeOfCare','ExpansionProfile','ExplanationOfBenefit','FamilyMemberHistory','Flag','Goal','GraphDefinition','Group','GuidanceResponse','HealthcareService','ImagingManifest','ImagingStudy','Immunization','ImmunizationRecommendation','ImplementationGuide','Library','Linkage','List','Location','Measure','MeasureReport','Media','Medication','MedicationAdministration','MedicationDispense','MedicationRequest','MedicationStatement','MessageDefinition','MessageHeader','NamingSystem','NutritionOrder','Observation','OperationDefinition','OperationOutcome','Organization','Parameters','Patient','PaymentNotice','PaymentReconciliation','Person','PlanDefinition','Practitioner','PractitionerRole','Procedure','ProcedureRequest','ProcessRequest','ProcessResponse','Provenance','Questionnaire','QuestionnaireResponse','ReferralRequest','RelatedPerson','RequestGroup','ResearchStudy','ResearchSubject','RiskAssessment','Schedule','SearchParameter','Sequence','ServiceDefinition','Slot','Specimen','StructureDefinition','StructureMap','Subscription','Substance','SupplyDelivery','SupplyRequest','Task','TestReport','TestScript','ValueSet','VisionPrescription'])
# interaction types
@pytest.mark.parametrize("include_type", ['history-instance','vread','read','delete','search-type','create','update','history-type'])


def test_resource_interaction(host, resource, include_type):
    capability_statement = get_capability_statement(host)
    #pdb.set_trace()
    assert len(capability_statement['rest']) == 1
    resources = []
    total_resource_list = []

    res = get_resource(host, resource)
    #print(capability_statement['rest'][0]['resource'])
    #resources = [res for res in capability_statement['rest'][0]['resource'] if res['type'] == resource]
    #assert len(resources) == 1

    matching_codes = [ x['code'] for x in res['interaction'] ]
    assert include_type in matching_codes, f"Supports {resource}.{include_type}" 

