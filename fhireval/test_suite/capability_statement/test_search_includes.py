

import pytest
from fhireval.test_suite.capability_statement import get_resource, get_capability_statement


# Which bullet point do these tests map to
test_id = f"{'2.1.3':<10} - Search Includes"

# How much weight do we attribute to the tests in this file
test_weight = 2

@pytest.mark.capability_statement

# searchInclude
@pytest.mark.parametrize("si_res, search_includes", [
	('Account', ['Account:patient', 'Account:subject', 'Account:owner']),
	('ActivityDefinition', ['ActivityDefinition:successor', 'ActivityDefinition:predecessor', 'ActivityDefinition:derived-from', 'ActivityDefinition:depends-on', 'ActivityDefinition:composed-of']),
	('AdverseEvent', ['AdverseEvent:substance', 'AdverseEvent:subject', 'AdverseEvent:study', 'AdverseEvent:location', 'AdverseEvent:reaction', 'AdverseEvent:recorder']),
	('AllergyIntolerance', ['AllergyIntolerance:patient', 'AllergyIntolerance:recorder', 'AllergyIntolerance:asserter']),
	('Appointment', ['Appointment:practitioner', 'Appointment:patient', 'Appointment:location', 'Appointment:incomingreferral', 'Appointment:actor']),
	('AppointmentResponse', ['AppointmentResponse:location', 'AppointmentResponse:patient', 'AppointmentResponse:practitioner', 'AppointmentResponse:actor', 'AppointmentResponse:appointment']),
	('AuditEvent', ['AuditEvent:patient', 'AuditEvent:entity', 'AuditEvent:agent']),
	('Basic', ['Basic:patient', 'Basic:subject', 'Basic:author']),
	('Binary', []),
	('BodySite', ['BodySite:patient']),
	('Bundle', ['Bundle:message', 'Bundle:composition']),
	('CapabilityStatement', ['CapabilityStatement:supported-profile', 'CapabilityStatement:resource-profile']),
	('CarePlan', ['CarePlan:patient', 'CarePlan:subject', 'CarePlan:part-of', 'CarePlan:replaces', 'CarePlan:context', 'CarePlan:performer', 'CarePlan:condition', 'CarePlan:encounter', 'CarePlan:goal', 'CarePlan:definition', 'CarePlan:care-team', 'CarePlan:activity-reference', 'CarePlan:based-on', 'CarePlan:author-inc']),
	('CareTeam', ['CareTeam:patient', 'CareTeam:subject', 'CareTeam:context', 'CareTeam:participant', 'CareTeam:encounter']),
	('ChargeItem', ['ChargeItem:requesting-organization', 'ChargeItem:subject', 'ChargeItem:service', 'ChargeItem:performing-organization', 'ChargeItem:participant-actor', 'ChargeItem:patient', 'ChargeItem:enterer', 'ChargeItem:account', 'ChargeItem:context']),
	('Claim', ['Claim:insurer', 'Claim:payee', 'Claim:patient', 'Claim:organization', 'Claim:facility', 'Claim:provider', 'Claim:enterer', 'Claim:encounter', 'Claim:care-team']),
	('ClaimResponse', ['ClaimResponse:request', 'ClaimResponse:insurer', 'ClaimResponse:request-provider', 'ClaimResponse:patient']),
	('ClinicalImpression', ['ClinicalImpression:patient', 'ClinicalImpression:subject', 'ClinicalImpression:problem', 'ClinicalImpression:previous', 'ClinicalImpression:investigation', 'ClinicalImpression:finding-ref', 'ClinicalImpression:context', 'ClinicalImpression:assessor', 'ClinicalImpression:action']),
	('CodeSystem', []),
	('Communication', ['Communication:subject', 'Communication:encounter', 'Communication:sender', 'Communication:patient', 'Communication:recipient', 'Communication:part-of', 'Communication:definition', 'Communication:based-on', 'Communication:context']),
	('CommunicationRequest', ['CommunicationRequest:subject', 'CommunicationRequest:replaces', 'CommunicationRequest:recipient', 'CommunicationRequest:requester', 'CommunicationRequest:sender', 'CommunicationRequest:patient', 'CommunicationRequest:context', 'CommunicationRequest:encounter', 'CommunicationRequest:based-on']),
	('CompartmentDefinition', []),
	('Composition', ['Composition:patient', 'Composition:subject', 'Composition:related-ref', 'Composition:entry', 'Composition:attester', 'Composition:author', 'Composition:encounter']),
	('ConceptMap', ['ConceptMap:source', 'ConceptMap:source-uri', 'ConceptMap:target', 'ConceptMap:target-uri']),
	('Condition', ['Condition:patient', 'Condition:subject', 'Condition:encounter', 'Condition:context', 'Condition:evidence-detail', 'Condition:asserter']),
	('Consent', ['Consent:patient', 'Consent:source', 'Consent:organization', 'Consent:consentor', 'Consent:data', 'Consent:actor']),
	('Contract', ['Contract:term-topic', 'Contract:subject', 'Contract:domain', 'Contract:patient', 'Contract:agent', 'Contract:signer', 'Contract:authority']),
	('Coverage', ['Coverage:subscriber', 'Coverage:policy-holder', 'Coverage:payor', 'Coverage:beneficiary']),
	('DataElement', []),
	('DetectedIssue', ['DetectedIssue:patient', 'DetectedIssue:author', 'DetectedIssue:implicated']),
	('Device', ['Device:organization', 'Device:patient', 'Device:location']),
	('DeviceComponent', ['DeviceComponent:source', 'DeviceComponent:parent']),
	('DeviceMetric', ['DeviceMetric:source', 'DeviceMetric:parent']),
	('DeviceRequest', ['DeviceRequest:patient', 'DeviceRequest:performer', 'DeviceRequest:subject', 'DeviceRequest:requester', 'DeviceRequest:priorrequest', 'DeviceRequest:definition', 'DeviceRequest:device', 'DeviceRequest:based-on', 'DeviceRequest:encounter']),
	('DeviceUseStatement', ['DeviceUseStatement:patient', 'DeviceUseStatement:subject', 'DeviceUseStatement:device']),
	('DiagnosticReport', ['DiagnosticReport:patient', 'DiagnosticReport:result', 'DiagnosticReport:subject', 'DiagnosticReport:image', 'DiagnosticReport:specimen', 'DiagnosticReport:performer', 'DiagnosticReport:context', 'DiagnosticReport:based-on', 'DiagnosticReport:encounter']),
	('DocumentManifest', ['DocumentManifest:patient', 'DocumentManifest:related-ref', 'DocumentManifest:subject', 'DocumentManifest:recipient', 'DocumentManifest:content-ref', 'DocumentManifest:author']),
	('DocumentReference', ['DocumentReference:patient', 'DocumentReference:subject', 'DocumentReference:related-ref', 'DocumentReference:relatesto', 'DocumentReference:custodian', 'DocumentReference:author', 'DocumentReference:authenticator', 'DocumentReference:encounter']),
	('EligibilityRequest', ['EligibilityRequest:patient', 'EligibilityRequest:organization', 'EligibilityRequest:provider', 'EligibilityRequest:facility', 'EligibilityRequest:enterer']),
	('EligibilityResponse', ['EligibilityResponse:request-organization', 'EligibilityResponse:request-provider', 'EligibilityResponse:request', 'EligibilityResponse:insurer']),
	('Encounter', ['Encounter:patient', 'Encounter:service-provider', 'Encounter:subject', 'Encounter:practitioner', 'Encounter:participant', 'Encounter:part-of', 'Encounter:location', 'Encounter:episodeofcare', 'Encounter:diagnosis', 'Encounter:incomingreferral', 'Encounter:appointment']),
	('Endpoint', ['Endpoint:organization']),
	('EnrollmentRequest', ['EnrollmentRequest:patient', 'EnrollmentRequest:subject', 'EnrollmentRequest:organization']),
	('EnrollmentResponse', ['EnrollmentResponse:request', 'EnrollmentResponse:organization']),
	('EpisodeOfCare', ['EpisodeOfCare:patient', 'EpisodeOfCare:condition', 'EpisodeOfCare:incomingreferral', 'EpisodeOfCare:organization', 'EpisodeOfCare:care-manager']),
	('ExpansionProfile', []),
	('ExplanationOfBenefit', ['ExplanationOfBenefit:payee', 'ExplanationOfBenefit:provider', 'ExplanationOfBenefit:claim', 'ExplanationOfBenefit:patient', 'ExplanationOfBenefit:organization', 'ExplanationOfBenefit:encounter', 'ExplanationOfBenefit:coverage', 'ExplanationOfBenefit:facility', 'ExplanationOfBenefit:enterer', 'ExplanationOfBenefit:care-team']),
	('FamilyMemberHistory', ['FamilyMemberHistory:patient', 'FamilyMemberHistory:definition']),
	('Flag', ['Flag:patient', 'Flag:subject', 'Flag:author', 'Flag:encounter']),
	('Goal', ['Goal:patient', 'Goal:subject']),
	('GraphDefinition', []),
	('Group', ['Group:member']),
	('GuidanceResponse', ['GuidanceResponse:patient', 'GuidanceResponse:subject']),
	('HealthcareService', ['HealthcareService:organization', 'HealthcareService:endpoint', 'HealthcareService:location']),
	('ImagingManifest', ['ImagingManifest:patient', 'ImagingManifest:imaging-study', 'ImagingManifest:endpoint', 'ImagingManifest:author']),
	('ImagingStudy', ['ImagingStudy:patient', 'ImagingStudy:performer', 'ImagingStudy:endpoint', 'ImagingStudy:context', 'ImagingStudy:basedon']),
	('Immunization', ['Immunization:patient', 'Immunization:practitioner', 'Immunization:reaction', 'Immunization:location', 'Immunization:manufacturer']),
	('ImmunizationRecommendation', ['ImmunizationRecommendation:support', 'ImmunizationRecommendation:patient', 'ImmunizationRecommendation:information']),
	('ImplementationGuide', ['ImplementationGuide:resource']),
	('Library', ['Library:successor', 'Library:predecessor', 'Library:derived-from', 'Library:composed-of', 'Library:depends-on']),
	('Linkage', ['Linkage:author']),
	('List', ['List:patient', 'List:subject', 'List:item', 'List:source', 'List:encounter']),
	('Location', ['Location:partof', 'Location:organization', 'Location:endpoint']),
	('Measure', ['Measure:successor', 'Measure:predecessor', 'Measure:composed-of', 'Measure:derived-from', 'Measure:depends-on']),
	('MeasureReport', ['MeasureReport:patient']),
	('Media', ['Media:subject', 'Media:patient', 'Media:operator', 'Media:context', 'Media:based-on', 'Media:device']),
	('Medication', ['Medication:package-item', 'Medication:manufacturer', 'Medication:ingredient']),
	('MedicationAdministration', ['MedicationAdministration:subject', 'MedicationAdministration:prescription', 'MedicationAdministration:performer', 'MedicationAdministration:patient', 'MedicationAdministration:medication', 'MedicationAdministration:device', 'MedicationAdministration:context']),
	('MedicationDispense', ['MedicationDispense:subject', 'MedicationDispense:receiver', 'MedicationDispense:responsibleparty', 'MedicationDispense:performer', 'MedicationDispense:context', 'MedicationDispense:destination', 'MedicationDispense:prescription', 'MedicationDispense:patient', 'MedicationDispense:medication']),
	('MedicationRequest', ['MedicationRequest:requester', 'MedicationRequest:subject', 'MedicationRequest:intended-dispenser', 'MedicationRequest:context', 'MedicationRequest:patient', 'MedicationRequest:medication']),
	('MedicationStatement', ['MedicationStatement:subject', 'MedicationStatement:source', 'MedicationStatement:context', 'MedicationStatement:part-of', 'MedicationStatement:patient', 'MedicationStatement:medication']),
	('MessageDefinition', []),
	('MessageHeader', ['MessageHeader:target', 'MessageHeader:responsible', 'MessageHeader:sender', 'MessageHeader:focus', 'MessageHeader:receiver', 'MessageHeader:enterer', 'MessageHeader:author']),
	('NamingSystem', ['NamingSystem:replaced-by']),
	('NutritionOrder', ['NutritionOrder:patient', 'NutritionOrder:provider', 'NutritionOrder:encounter']),
	('Observation', ['Observation:patient', 'Observation:specimen', 'Observation:subject', 'Observation:related-target', 'Observation:performer', 'Observation:device', 'Observation:context', 'Observation:based-on', 'Observation:encounter']),
	('OperationDefinition', ['OperationDefinition:param-profile', 'OperationDefinition:base']),
	('OperationOutcome', []),
	('Organization', ['Organization:partof', 'Organization:endpoint']),
	('Parameters', []),
	('Patient', ['Patient:general-practitioner', 'Patient:organization', 'Patient:link']),
	('PaymentNotice', ['PaymentNotice:request', 'PaymentNotice:provider', 'PaymentNotice:response', 'PaymentNotice:organization']),
	('PaymentReconciliation', ['PaymentReconciliation:request', 'PaymentReconciliation:request-provider', 'PaymentReconciliation:request-organization', 'PaymentReconciliation:organization']),
	('Person', ['Person:relatedperson', 'Person:patient', 'Person:practitioner', 'Person:organization', 'Person:link']),
	('PlanDefinition', ['PlanDefinition:successor', 'PlanDefinition:predecessor', 'PlanDefinition:derived-from', 'PlanDefinition:depends-on', 'PlanDefinition:composed-of']),
	('Practitioner', []),
	('PractitionerRole', ['PractitionerRole:service', 'PractitionerRole:organization', 'PractitionerRole:practitioner', 'PractitionerRole:location', 'PractitionerRole:endpoint']),
	('Procedure', ['Procedure:patient', 'Procedure:performer', 'Procedure:subject', 'Procedure:part-of', 'Procedure:location', 'Procedure:context', 'Procedure:based-on', 'Procedure:definition', 'Procedure:encounter']),
	('ProcedureRequest', ['ProcedureRequest:patient', 'ProcedureRequest:requester', 'ProcedureRequest:replaces', 'ProcedureRequest:subject', 'ProcedureRequest:specimen', 'ProcedureRequest:performer', 'ProcedureRequest:definition', 'ProcedureRequest:based-on', 'ProcedureRequest:context', 'ProcedureRequest:encounter']),
	('ProcessRequest', ['ProcessRequest:provider', 'ProcessRequest:organization']),
	('ProcessResponse', ['ProcessResponse:request-provider', 'ProcessResponse:request', 'ProcessResponse:organization', 'ProcessResponse:request-organization']),
	('Provenance', ['Provenance:location', 'Provenance:patient', 'Provenance:target', 'Provenance:entity-ref', 'Provenance:agent']),
	('Questionnaire', []),
	('QuestionnaireResponse', ['QuestionnaireResponse:questionnaire', 'QuestionnaireResponse:subject', 'QuestionnaireResponse:source', 'QuestionnaireResponse:patient', 'QuestionnaireResponse:parent', 'QuestionnaireResponse:context', 'QuestionnaireResponse:based-on', 'QuestionnaireResponse:author']),
	('ReferralRequest', ['ReferralRequest:patient', 'ReferralRequest:recipient', 'ReferralRequest:requester', 'ReferralRequest:replaces', 'ReferralRequest:subject', 'ReferralRequest:definition', 'ReferralRequest:encounter', 'ReferralRequest:context', 'ReferralRequest:based-on']),
	('RelatedPerson', ['RelatedPerson:patient']),
	('RequestGroup', ['RequestGroup:subject', 'RequestGroup:patient', 'RequestGroup:participant', 'RequestGroup:encounter', 'RequestGroup:definition', 'RequestGroup:context', 'RequestGroup:author']),
	('ResearchStudy', ['ResearchStudy:sponsor', 'ResearchStudy:site', 'ResearchStudy:protocol', 'ResearchStudy:principalinvestigator', 'ResearchStudy:partof']),
	('ResearchSubject', ['ResearchSubject:individual', 'ResearchSubject:patient']),
	('RiskAssessment', ['RiskAssessment:patient', 'RiskAssessment:performer', 'RiskAssessment:condition', 'RiskAssessment:subject', 'RiskAssessment:encounter']),
	('Schedule', ['Schedule:actor']),
	('SearchParameter', ['SearchParameter:component']),
	('Sequence', ['Sequence:patient']),
	('ServiceDefinition', ['ServiceDefinition:successor', 'ServiceDefinition:predecessor', 'ServiceDefinition:depends-on', 'ServiceDefinition:composed-of', 'ServiceDefinition:derived-from']),
	('Slot', ['Slot:schedule']),
	('Specimen', ['Specimen:subject', 'Specimen:patient', 'Specimen:parent', 'Specimen:collector']),
	('StructureDefinition', ['StructureDefinition:valueset']),
	('StructureMap', []),
	('Subscription', []),
	('Substance', ['Substance:substance-reference']),
	('SupplyDelivery', ['SupplyDelivery:patient', 'SupplyDelivery:supplier', 'SupplyDelivery:receiver']),
	('SupplyRequest', ['SupplyRequest:supplier', 'SupplyRequest:requester']),
	('Task', ['Task:subject', 'Task:requester', 'Task:part-of', 'Task:patient', 'Task:organization', 'Task:owner', 'Task:based-on', 'Task:context', 'Task:focus']),
	('TestReport', ['TestReport:testscript']),
	('TestScript', []),
	('ValueSet', []),
	('VisionPrescription', ['VisionPrescription:patient', 'VisionPrescription:prescriber', 'VisionPrescription:encounter'])
])



def test_search_includes(host, si_res, search_includes):
    res = get_resource(host, si_res)
    includes = set(res['searchInclude'])

    for inc in search_includes:
        assert inc in includes, f"Does searchInclude({inc})?"


