import sys
import ctypes
class MotorDriveType:
	# Configures the motor to coast
	MOTOR_DRIVE_TYPE_COAST = 1
	# Configures the motor for active control
	MOTOR_DRIVE_TYPE_ACTIVE = 2

	@classmethod
	def getName(self, val):
		if val == self.MOTOR_DRIVE_TYPE_COAST:
			return "MOTOR_DRIVE_TYPE_COAST"
		if val == self.MOTOR_DRIVE_TYPE_ACTIVE:
			return "MOTOR_DRIVE_TYPE_ACTIVE"
		return "<invalid enumeration value>"
