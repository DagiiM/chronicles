from enum import Enum

class Gender(Enum):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'


class StaffStatus(Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    TERMINATED = 'Terminated'

class Specialty(Enum):
    CARDIOLOGIST = 'cardiologist', 'Cardiologist'
    DERMATOLOGIST = 'dermatologist', 'Dermatologist'
    ENDOCRINOLOGIST = 'endocrinologist', 'Endocrinologist'
    GYNECOLOGIST = 'gynecologist', 'Gynecologist'
    NEUROLOGIST = 'neurologist', 'Neurologist'
    PSYCHIATRIST = 'psychiatrist', 'Psychiatrist'
    SURGEON = 'surgeon', 'Surgeon'
    UROLOGIST = 'urologist', 'Urologist'
    
class AppointmentStatus(Enum):
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"
    RESCHEDULED = "rescheduled"


class ContractStatus(Enum):
    ACTIVE = 'Active'
    PENDING = 'Pending'
    EXPIRED = 'Expired'
    TERMINATED = 'Terminated'

class Status(Enum):
    """
    Enum representing the status of staff.
    """
    REQUESTED = 'Requested'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    
    
class LeaveType(Enum):
    SICK_LEAVE = 'Sick leave'
    MATERNITY_LEAVE = 'Maternity leave'
    PATERNITY_LEAVE = 'Paternity leave'
    ANNUAL_LEAVE = 'Annual leave'
    COMPASSIONATE_LEAVE = 'Compassionate leave'
    STUDY_LEAVE = 'Study leave'
    JURY_DUTY_LEAVE = 'Jury duty leave'
    PUBLIC_HOLIDAY_LEAVE = 'Public holiday leave'
    UNPAID_LEAVE = 'Unpaid leave'
    PERSONAL_LEAVE = 'Personal leave'