import sys
import ctypes
class MotorPositionType:
	# Configures the controller to use the encoder as a position source
	MOTOR_POSITION_TYPE_ENCODER = 1
	# Configures the controller to use the hall-effect sensor as a position source
	MOTOR_POSITION_TYPE_HALL = 2

	@classmethod
	def getName(self, val):
		if val == self.MOTOR_POSITION_TYPE_ENCODER:
			return "MOTOR_POSITION_TYPE_ENCODER"
		if val == self.MOTOR_POSITION_TYPE_HALL:
			return "MOTOR_POSITION_TYPE_HALL"
		return "<invalid enumeration value>"
