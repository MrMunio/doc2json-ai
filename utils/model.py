from typing import List, Optional
from pydantic import BaseModel, Field

class ContractMetadata(BaseModel):
    contract_title: Optional[str] = Field(None, description="Full title of the agreement")
    contract_type: Optional[str] = Field(None, description='Type of contract (e.g., "BH I/DD Tailored Plan Provider Contract")')
    document_name: Optional[str] = Field(None, description="Document template name")
    contract_version: Optional[str] = Field(None, description="Version number")
    effective_date: Optional[str] = Field(None, description="When the contract becomes effective")
    initial_term_years: Optional[int] = Field(None, description="Length of initial term in years")
    renewal_term_years: Optional[int] = Field(None, description="Length of renewal terms in years")
    auto_renewal: Optional[bool] = Field(None, description="Boolean - does it automatically renew?")
    reference_number: Optional[str] = Field(None, description="Contract reference or ECM number")
    company_signature_date: Optional[str] = Field(None, description="Date company signs")
    provider_signature_date: Optional[str] = Field(None, description="Date provider signs")
    governing_contract: Optional[str] = Field(None, description="Name of parent/governing contract")
    contract_limitation: Optional[str] = Field(None, description="Any limitations on contract duration")

class CompanyInformation(BaseModel):
    company_legal_name: Optional[str] = Field(None, description="Full legal name of the company")
    company_entity_type: Optional[str] = Field(None, description='Type of entity (e.g., "local political subdivision")')
    company_product_type: Optional[str] = Field(None, description="Product or plan type")
    company_contact_name: Optional[str] = Field(None, description="Primary contact person")
    company_contact_title: Optional[str] = Field(None, description="Contact person's title")
    company_contact_address: Optional[str] = Field(None, description="Company address")
    company_authorized_signatory_name: Optional[str] = Field(None, description="Name of person authorized to sign")
    company_authorized_signatory_title: Optional[str] = Field(None, description="Title of authorized signatory")
    company_state_jurisdiction: Optional[str] = Field(None, description="State of jurisdiction")
    company_fraud_hotline: Optional[str] = Field(None, description="Fraud reporting hotline number")

class ProviderInformation(BaseModel):
    provider_legal_name: Optional[str] = Field(None, description="Provider's full legal name")
    provider_type: Optional[str] = Field(None, description="Type of provider")
    provider_contact_name: Optional[str] = Field(None, description="Primary contact")
    provider_contact_address: Optional[str] = Field(None, description="Provider address")
    provider_authorized_signatory_name: Optional[str] = Field(None, description="Authorized signatory name")
    provider_authorized_signatory_title: Optional[str] = Field(None, description="Authorized signatory title")
    provider_tin: Optional[str] = Field(None, description="Tax Identification Number")
    provider_state_medicaid_number: Optional[str] = Field(None, description="State Medicaid number")
    provider_npi: Optional[str] = Field(None, description="National Provider Identifier")
    provider_state_license_number: Optional[str] = Field(None, description="State license number")
    provider_office_phone: Optional[str] = Field(None, description="Office telephone number(s)")
    provider_hospital_affiliations: Optional[str] = Field(None, description="Hospital affiliations")
    provider_specialties: Optional[str] = Field(None, description="Provider specialties")
    provider_board_status: Optional[str] = Field(None, description="Board certification status")

class ServiceStandards(BaseModel):
    mobile_crisis_response_time: Optional[str] = Field(None, description="Response time for mobile crisis services")
    facility_crisis_availability: Optional[str] = Field(None, description="Availability for facility-based crisis")
    emergency_mental_health_availability: Optional[str] = Field(None, description="Emergency mental health availability")
    emergency_sud_availability: Optional[str] = Field(None, description="Emergency SUD services availability")
    general_appointment_standards: Optional[str] = Field(None, description="General appointment access standards")

class CoveredServices(BaseModel):
    covered_services_description: Optional[str] = Field(None, description="Description of covered services")
    care_standards: Optional[List[str]] = Field(None, description="Standards for providing care")
    service_location_restrictions: Optional[str] = Field(None, description="Any restrictions on service locations")
    scope_of_license: Optional[str] = Field(None, description="Services within scope of provider license")

class CompensationPayment(BaseModel):
    compensation_basis: Optional[str] = Field(None, description='How compensation is determined (e.g., "Compensation Schedule in effect on date of service")')
    payment_acceptance_terms: Optional[str] = Field(None, description="Terms for accepting payment")
    payment_method: Optional[str] = Field(None, description='Required payment method (e.g., "EFT-ACH")')
    payment_deductions: Optional[List[str]] = Field(None, description="List of allowable deductions (copays, cost-sharing)")
    clean_claim_definition: Optional[str] = Field(None, description="Definition of clean claim")
    financial_incentive_prohibition: Optional[str] = Field(None, description="Any prohibition on withholding services")

class ClaimsProcessing(BaseModel):
    claims_submission_requirement: Optional[str] = Field(None, description="How claims must be submitted")
    encounter_data_required: Optional[bool] = Field(None, description="Is encounter data required?")
    encounter_data_elements: Optional[List[str]] = Field(None, description="Required data elements (member info, diagnosis codes, etc.)")
    claims_denial_risk: Optional[str] = Field(None, description="Conditions under which claims may be denied")
    claims_processing_timeline: Optional[str] = Field(None, description="Timeline for processing clean claims")
    late_payment_provisions: Optional[str] = Field(None, description="Provisions for late payments")

class HoldHarmless(BaseModel):
    hold_harmless_provider_obligation: Optional[str] = Field(None, description="Provider's hold harmless obligation")
    hold_harmless_triggering_events: Optional[List[str]] = Field(None, description="Events that trigger hold harmless (insolvency, non-payment, breach)")
    hold_harmless_exceptions: Optional[List[str]] = Field(None, description="Exceptions (copays, cost-sharing)")
    hold_harmless_survival: Optional[bool] = Field(None, description="Does it survive contract termination?")

class RecoveryRecoupment(BaseModel):
    offset_recoupment_notice_period: Optional[str] = Field(None, description='Notice period for offset/recoupment (e.g., "30 days")')
    recoupment_timeframe: Optional[str] = Field(None, description='Timeframe within which recoupment can occur (e.g., "2 years")')
    recoupment_exceptions: Optional[List[str]] = Field(None, description="Exceptions (fraud, government payor)")
    standard_recoupment_definition: Optional[str] = Field(None, description="What constitutes standard recoupment")
    non_standard_recoupment_definition: Optional[str] = Field(None, description="What constitutes non-standard recoupment")
    non_standard_recoupment_notice: Optional[str] = Field(None, description="Notice requirements for non-standard")
    appeals_process: Optional[str] = Field(None, description="How to appeal recoupment decisions")

class Credentialing(BaseModel):
    credentialing_required: Optional[bool] = Field(None, description="Is credentialing required?")
    recredentialing_required: Optional[bool] = Field(None, description="Is recredentialing required?")
    credentialing_compliance: Optional[str] = Field(None, description="Requirements for Regulatory Requirements")
    accreditation_bodies: Optional[List[str]] = Field(None, description='Required accreditation bodies (e.g., "Joint Commission")')
    medicare_participation_required: Optional[bool] = Field(None, description="Must be Medicare participating provider?")
    medicaid_participation_required: Optional[bool] = Field(None, description="Must be Medicaid participating provider?")
    commencement_restriction: Optional[str] = Field(None, description="Can provider start before credentialing approval?")

class ProviderManual(BaseModel):
    provider_manual_areas: Optional[List[str]] = Field(None, description="List of areas covered by Provider Manual")
    provider_manual_availability: Optional[str] = Field(None, description="How/when Provider Manual is made available")
    provider_manual_amendment_notice: Optional[str] = Field(None, description="How amendments are communicated")
    provider_manual_amendment_effective_period: Optional[str] = Field(None, description='When amendments become effective (e.g., "15 days")')

class EligibilityVerification(BaseModel):
    eligibility_verification_requirement: Optional[str] = Field(None, description="Must provider verify eligibility?")
    eligibility_verification_method: Optional[str] = Field(None, description="How to verify eligibility")
    eligibility_limitations: Optional[List[str]] = Field(None, description="Limitations on eligibility guarantees")

class ReferralPreauthorization(BaseModel):
    referral_preauth_requirement: Optional[str] = Field(None, description="Are referrals/preauthorizations required?")
    referral_preauth_timing: Optional[str] = Field(None, description="When must referral/preauth occur?")
    referral_preauth_failure_consequence: Optional[str] = Field(None, description="What happens if requirements not met?")
    referral_restriction: Optional[str] = Field(None, description='Restrictions on referrals (e.g., "only to Participating Providers")')

class ComplianceRegulatory(BaseModel):
    hipaa_compliance_required: Optional[bool] = Field(None, description="HIPAA compliance required?")
    fraud_waste_abuse_laws: Optional[List[str]] = Field(None, description="List of fraud, waste, abuse laws (False Claims Act, Anti-Kickback, etc.)")
    fraud_reporting_hotline: Optional[str] = Field(None, description="Hotline for reporting fraud")
    fraud_reporting_anonymous: Optional[bool] = Field(None, description="Can reports be made anonymously?")
    compliance_program_requirements: Optional[str] = Field(None, description="Requirements for compliance program")
    compliance_audit_rights: Optional[str] = Field(None, description="Company's rights to audit for compliance")
    compliance_audit_cooperation: Optional[str] = Field(None, description="Provider's obligation to cooperate with audits")
    compliance_sanctions_offset: Optional[str] = Field(None, description="Can sanctions be offset against payments?")

class ProgramIntegrity(BaseModel):
    cfr_455_105_requirement: Optional[str] = Field(None, description="42 C.F.R. §455.105 disclosure requirements")
    cfr_455_104_requirement: Optional[str] = Field(None, description="42 C.F.R. §455.104 disclosure requirements")
    cfr_455_106_requirement: Optional[str] = Field(None, description="42 C.F.R. §455.106 disclosure requirements")
    disclosure_timing: Optional[str] = Field(None, description="When disclosures must be provided")

class IneligiblePersons(BaseModel):
    ineligible_person_warranty_period: Optional[List[str]] = Field(None, description="When warranty applies")
    ineligible_person_representation: Optional[str] = Field(None, description="What provider represents about ineligible persons")
    ineligible_person_definition: Optional[str] = Field(None, description="Definition of ineligible person")

class Nondiscrimination(BaseModel):
    protected_characteristics: Optional[List[str]] = Field(None, description="List of protected characteristics")
    accessibility_requirement: Optional[str] = Field(None, description='Accessibility requirements (e.g., "ADA Title III")')
    lgbtq_affirmation_requirement: Optional[str] = Field(None, description="Requirements for LGBTQ affirmation")
    equal_opportunity_compliance: Optional[str] = Field(None, description="Equal opportunity/affirmative action requirements")

class NoticeRequirements(BaseModel):
    notice_10_day_events: Optional[List[str]] = Field(None, description="Events requiring 10-day notice")
    notice_30_day_events: Optional[List[str]] = Field(None, description="Events requiring 30-day notice")
    notice_recipient: Optional[str] = Field(None, description="To whom notices must be sent")
    notice_format: Optional[List[str]] = Field(None, description="Format for notices (written, electronic, etc.)")

class Insurance(BaseModel):
    general_liability_per_occurrence: Optional[str] = Field(None, description="General liability per occurrence amount")
    general_liability_annual_aggregate: Optional[str] = Field(None, description="General liability annual aggregate amount")
    professional_liability_per_occurrence: Optional[str] = Field(None, description="Professional liability per occurrence")
    professional_liability_annual_aggregate: Optional[str] = Field(None, description="Professional liability annual aggregate")
    tail_coverage_required: Optional[bool] = Field(None, description="Is tail coverage required?")
    insurance_carrier_requirements: Optional[str] = Field(None, description="Requirements for insurance carrier")
    insurance_notice_of_changes_period: Optional[str] = Field(None, description='Notice period for insurance changes (e.g., "15 days")')

class RecordsInspections(BaseModel):
    record_types_required: Optional[List[str]] = Field(None, description="Types of records required (medical, financial, administrative)")
    record_standards: Optional[str] = Field(None, description="Standards for record-keeping")
    access_parties: Optional[List[str]] = Field(None, description="Who has access rights to records")
    access_conditions: Optional[List[str]] = Field(None, description="Conditions for access (business hours, prior notice)")
    copying_cost: Optional[str] = Field(None, description="Cost for providing copies")
    on_site_inspection_rights: Optional[str] = Field(None, description="Rights for on-site inspections")
    record_transfer_requirement: Optional[str] = Field(None, description="Requirements for transferring records")
    record_transfer_cost: Optional[str] = Field(None, description="Cost for record transfer")

class DataSecurity(BaseModel):
    phi_security_required: Optional[bool] = Field(None, description="Is PHI security required?")
    information_systems_security: Optional[str] = Field(None, description="Security requirements for Information Systems")
    minimum_security_measures: Optional[List[str]] = Field(None, description="List of minimum security measures")
    breach_definition: Optional[str] = Field(None, description="Definition of breach")
    breach_response_obligations: Optional[List[str]] = Field(None, description="Provider obligations when breach occurs")
    breach_notification_requirement: Optional[bool] = Field(None, description="Must Company be notified of breaches?")
    company_breach_liability: Optional[str] = Field(None, description="Is Company liable for Provider's breaches?")

class Indemnification(BaseModel):
    provider_indemnifies_company: Optional[bool] = Field(None, description="Does provider indemnify company?")
    provider_indemnification_scope: Optional[str] = Field(None, description="Scope of provider indemnification")
    provider_indemnification_triggers: Optional[List[str]] = Field(None, description="What triggers provider indemnification")
    company_indemnifies_provider: Optional[bool] = Field(None, description="Does company indemnify provider?")
    company_indemnification_scope: Optional[str] = Field(None, description="Scope of company indemnification")
    company_indemnification_triggers: Optional[List[str]] = Field(None, description="What triggers company indemnification")

class Termination(BaseModel):
    termination_upon_notice_period: Optional[str] = Field(None, description='Notice period for termination without cause (e.g., "120 days")')
    termination_with_cause_notice_period: Optional[str] = Field(None, description='Notice period for termination with cause (e.g., "90 days")')
    termination_with_cause_cure_period: Optional[str] = Field(None, description='Cure period for material breach (e.g., "60 days")')
    suspension_immediate: Optional[bool] = Field(None, description="Can participation be suspended immediately?")
    suspension_triggering_conditions: Optional[List[str]] = Field(None, description="What triggers immediate suspension")
    insolvency_termination_notice: Optional[str] = Field(None, description="Notice period for insolvency termination")
    credentialing_failure_termination: Optional[bool] = Field(None, description="Can provider be terminated for credentialing failure?")
    credentialing_termination_conditions: Optional[List[str]] = Field(None, description="Conditions for credentialing termination")
    post_termination_continuation_period: Optional[str] = Field(None, description='How long must services continue post-termination (e.g., "90 days")')
    post_termination_obligations: Optional[List[str]] = Field(None, description="Provider obligations after termination")

class NonRenewal(BaseModel):
    non_renewal_notice_period: Optional[str] = Field(None, description='Notice period for non-renewal (e.g., "180 days")')
    product_specific_non_renewal: Optional[bool] = Field(None, description="Can non-renewal be product-specific?")
    product_non_renewal_notice: Optional[str] = Field(None, description="Notice period for product-specific non-renewal")

class DisputeResolution(BaseModel):
    dispute_definition: Optional[str] = Field(None, description="What constitutes a dispute")
    dispute_step_1: Optional[str] = Field(None, description="First step in dispute resolution")
    dispute_step_2: Optional[str] = Field(None, description="Second step in dispute resolution")
    dispute_negotiation_period: Optional[str] = Field(None, description='Length of negotiation period (e.g., "60 days")')
    dispute_initiation_deadline: Optional[str] = Field(None, description='Deadline to initiate dispute (e.g., "within 1 year")')
    dispute_jurisdiction_state_court: Optional[str] = Field(None, description="State court with jurisdiction")
    dispute_jurisdiction_federal_court: Optional[str] = Field(None, description="Federal court with jurisdiction")

class SpecialProvisions(BaseModel):
    disparagement_prohibition: Optional[bool] = Field(None, description="Is disparagement prohibited?")
    disparagement_parties: Optional[List[str]] = Field(None, description="Who is bound by disparagement prohibition")
    disparagement_exceptions: Optional[List[str]] = Field(None, description="Exceptions to disparagement prohibition")
    use_of_name_authorization: Optional[str] = Field(None, description="Authorization for use of provider/company name")
    use_of_name_restrictions: Optional[str] = Field(None, description="Restrictions on use of names")
    treatment_decision_independence: Optional[str] = Field(None, description="Provider independence in treatment decisions")
    carve_out_services: Optional[str] = Field(None, description="Are there carved-out services?")
    third_party_vendor_cooperation: Optional[str] = Field(None, description="Requirements for third-party vendor cooperation")

class SchedulesAttachments(BaseModel):
    schedule_b_description: Optional[str] = Field(None, description="What is in Schedule B (Product Attachments)")
    schedule_c_description: Optional[str] = Field(None, description="What is in Schedule C (Contracted Providers list)")
    compensation_schedule_location: Optional[str] = Field(None, description="Where Compensation Schedule is located")
    product_attachments_purpose: Optional[str] = Field(None, description="Purpose of Product Attachments")
    provider_manual_reference: Optional[str] = Field(None, description="Reference to Provider Manual")

class ContractModel(BaseModel):
    contract_metadata: Optional[ContractMetadata] = None
    company_information: Optional[CompanyInformation] = None
    provider_information: Optional[ProviderInformation] = None
    service_standards: Optional[ServiceStandards] = None
    covered_services: Optional[CoveredServices] = None
    compensation_payment: Optional[CompensationPayment] = None
    claims_processing: Optional[ClaimsProcessing] = None
    hold_harmless: Optional[HoldHarmless] = None
    recovery_recoupment: Optional[RecoveryRecoupment] = None
    credentialing: Optional[Credentialing] = None
    provider_manual: Optional[ProviderManual] = None
    eligibility_verification: Optional[EligibilityVerification] = None
    referral_preauthorization: Optional[ReferralPreauthorization] = None
    compliance_regulatory: Optional[ComplianceRegulatory] = None
    program_integrity: Optional[ProgramIntegrity] = None
    ineligible_persons: Optional[IneligiblePersons] = None
    nondiscrimination: Optional[Nondiscrimination] = None
    notice_requirements: Optional[NoticeRequirements] = None
    insurance: Optional[Insurance] = None
    records_inspections: Optional[RecordsInspections] = None
    data_security: Optional[DataSecurity] = None
    indemnification: Optional[Indemnification] = None
    termination: Optional[Termination] = None
    non_renewal: Optional[NonRenewal] = None
    dispute_resolution: Optional[DisputeResolution] = None
    special_provisions: Optional[SpecialProvisions] = None
    schedules_attachments: Optional[SchedulesAttachments] = None