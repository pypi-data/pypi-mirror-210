class Compliance:
    def __init__(self, compliance_type, desc, r_type, cid):
        self._result = True
        self._failReason = ''
        self._offender = []
        self._compliance_type = compliance_type
        self._description = desc
        self._resource_type = r_type
        self._control_id = cid

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value: bool):
        self._result = value

    @property
    def failReason(self):
        return self._failReason

    @failReason.setter
    def failReason(self, reason: str):
        self._failReason = reason

    @property
    def offender(self):
        print("getter method")
        return self._offender

    @offender.setter
    def offender(self, offend: str):
        self._offender.append(offend)

    def compliance(self) -> dict:
        return {
            'Result': self._result,
            'failReason': self._failReason,
            'resource_type': self._resource_type,
            'Offenders': self._offender,
            'Compliance_type': self._compliance_type,
            'Description': self._description,
            'ControlId': self._control_id
        }

