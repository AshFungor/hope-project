import zoneinfo
import datetime
import string
import logging
import enum

import dateutil

# this is getting deployed near Moscow so this is hardcoded
CurrentTimezone = zoneinfo.ZoneInfo('Europe/Moscow')
# max human age confirmed, guess we will not see someone older
MaxDecline = dateutil.relativedelta.relativedelta(years=117)


class ValidationPolicy(enum.IntEnum):
    DISCARD = 0
    ABORT = 1
    IGNORE = 2


class StringValidator:
    
    def __init__(
        self, 
        policy: ValidationPolicy = ValidationPolicy.IGNORE, 
        allow_numbers: bool = True,
        allow_punctuation: bool = False,
        allow_whitespaces: bool = False,
        allow_latin_letters_lowercase: bool = True,
        allow_russian_letters_lowercase: bool = True,
        allow_russian_letters_uppercase: bool = True,
        allow_latin_letters_uppercase: bool = True,
        allow_additionally: str | None = None
    ) -> None:
        self.policy = policy
        
        allowed_chars = ''
        if allow_numbers:
            allowed_chars += string.digits
        if allow_punctuation:
            allowed_chars += string.punctuation
        if allow_whitespaces:
            allowed_chars += string.whitespace
        if allow_latin_letters_lowercase:
            allowed_chars += ''.join([chr(code) for code in range(ord('a'), ord('z') + 1)])
        if allow_latin_letters_uppercase:
            allowed_chars += ''.join([chr(code) for code in range(ord('A'), ord('Z') + 1)])
        if allow_russian_letters_lowercase:
            allowed_chars += ''.join([chr(code) for code in range(ord('а'), ord('я') + 1)])
        if allow_russian_letters_uppercase:
            allowed_chars += ''.join([chr(code) for code in range(ord('А'), ord('Я') + 1)])
        if allow_additionally:
            allowed_chars += ''.join(set(allow_additionally).difference(set(allowed_chars)))

        self.allowed_chars = set(allowed_chars)

    def validate(self, string: str, max_size: int, fixed: bool = False) -> str:
        validated = ''.join(filter(lambda char: char in self.allowed_chars, string))
        if self.policy == ValidationPolicy.IGNORE:
            if not self._validate_size(len(validated), len(string), max_size, fixed):
                logging.warn(f'string validator: {repr(self)}; string <{string}> did not pass validation, proposed: {validated}; IGNORING')
            return string
        if self.policy == ValidationPolicy.DISCARD:
            if not self._validate_size(len(validated), len(string), max_size, fixed):
                logging.warn(f'string validator: {repr(self)}; string <{string}> did not pass validation, proposed: {validated}; DISCARDING')
            return validated
        if self.policy == ValidationPolicy.ABORT:
            if not self._validate_size(len(validated), len(string), max_size, fixed):
                raise ValueError(f'error validating string: <{string}> did not pass validation, proposed: {validated}; ABORTING')
            return string
            
    def _validate_size(self, validated_size: int, initial_size: int, max_size: int, fixed: bool) -> False:
        if validated_size != initial_size:
            return False
        if validated_size > max_size:
            return False
        if validated_size != max_size and fixed:
            return False
        return True
    

class IntegerValidator:

    def __init__(self, policy: ValidationPolicy = ValidationPolicy.IGNORE) -> None:
        self.policy = policy

    def validate(self, integer: int, size: int, signed: bool = True) -> int:
        lower = upper = 0
        if signed:
            upper = (1 << (size - 1)) - 1
            lower = (1 << (size - 1)) * -1
        else:
            lower = 0
            upper = (1 << size) - 1
        validated = max(lower, min(upper, integer))

        if self.policy == ValidationPolicy.IGNORE:
            if validated != integer:
                logging.warn(f'integer validator: {repr(self)}; integer <{integer}> overflows; clamped: {validated}; IGNORING')
            return integer
        if self.policy == ValidationPolicy.DISCARD:
            if validated != integer:
                logging.warn(f'integer validator: {repr(self)}; integer <{integer}> overflows; clamped: {validated}; IGNORING')
            return validated
        if self.policy == ValidationPolicy.ABORT:
            if validated != integer:
                raise ValueError(f'error validating integer: <{integer}> did not pass validation, clamped: {validated}; ABORTING')
            return integer


class EnumerationValidator:
    
    def __init__(self, policy: ValidationPolicy = ValidationPolicy.IGNORE) -> None:
        self.policy = policy

    def validate(self, value: int | str, passed_enum: enum.IntEnum | enum.StrEnum, default: str | int | None = None) -> str | int:
        if not self._ensure_types(value, passed_enum, default):
            raise ValueError(f'type check failed for triple: {repr(value)}; {repr(passed_enum)}; {repr(default)}')
        for possible_value in passed_enum:
            if possible_value == value:
                return possible_value
        return self._fallback(f'value {value} not in enum values: ' + ''.join([*passed_enum]), value, default)

    def _ensure_types(self, value: int | str, passed_enum: enum.IntEnum | enum.StrEnum, default: str | int | None) -> bool:
        if isinstance(value, int):
            return issubclass(passed_enum, enum.IntEnum) and isinstance(default, (int, None))
        if isinstance(value, str):
            return issubclass(passed_enum, enum.StrEnum) and isinstance(default, (str, None))
        return False
    
    def _fallback(self, error_string: str, unmatched_value: int | str, default: int | str) -> int | str:
        if self.policy == ValidationPolicy.IGNORE:
            logging.warn(f'enum validator: {repr(self)}; ' + error_string + '; IGNORING')
            return unmatched_value
        if self.policy == ValidationPolicy.DISCARD:
            logging.warn(f'enum validator: {repr(self)}; ' + error_string + '; DISCARDING')
            return default
        if self.policy == ValidationPolicy.ABORT:
            raise ValueError(f'error validating enum value: <{unmatched_value}>;' + error_string + '; ABORTING')
        

class DatetimeValidator:

    def __init__(self, policy: ValidationPolicy = ValidationPolicy.IGNORE) -> None:
        self.policy = policy

    def validate(
        self, 
        target: datetime.datetime, 
        lower: datetime.datetime = datetime.datetime.now(CurrentTimezone) - MaxDecline, 
        upper: datetime.datetime = datetime.datetime.now(CurrentTimezone)
    ) -> datetime.datetime:
        validated = max(lower, min(upper, target))
        if validated != target:
            return self._fallback(f'datetime <{target}> out of bounds: from {lower} tp {upper}', target, validated)

    def _fallback(self, error_string: str, initial_target: datetime.datetime, validated_target: datetime.datetime) -> datetime.datetime:
        if self.policy == ValidationPolicy.IGNORE:
            logging.warn(f'datetime validator: {repr(self)}; ' + error_string + '; IGNORING')
            return initial_target
        if self.policy == ValidationPolicy.DISCARD:
            logging.warn(f'datetime validator: {repr(self)}; ' + error_string + '; DISCARDED')
            return validated_target
        if self.policy == ValidationPolicy.ABORT:
            raise ValueError(f'error validating datetime value: <{initial_target}>;' + error_string + '; ABORTING')


GenericTextValidator = StringValidator(
    ValidationPolicy.DISCARD, 
    allow_numbers=True,
    allow_punctuation=True,
    allow_whitespaces=False,
    allow_latin_letters_lowercase=True,
    allow_latin_letters_uppercase=True,
    allow_russian_letters_lowercase=True,
    allow_russian_letters_uppercase=True,
    allow_additionally=' '
)

PureRussianTextValidator = StringValidator(
    ValidationPolicy.DISCARD, 
    allow_numbers=True,
    allow_punctuation=False,
    allow_whitespaces=False,
    allow_latin_letters_lowercase=False,
    allow_latin_letters_uppercase=False,
    allow_russian_letters_lowercase=True,
    allow_russian_letters_uppercase=True,
    allow_additionally=' '
)

NoWhitespaceGenericTextValidator = StringValidator(
    ValidationPolicy.DISCARD, 
    allow_numbers=True,
    allow_punctuation=True,
    allow_whitespaces=False,
    allow_latin_letters_lowercase=True,
    allow_latin_letters_uppercase=True,
    allow_russian_letters_lowercase=True,
    allow_russian_letters_uppercase=True,
    allow_additionally=''
)

NoPunctuationGenericTextValidator = StringValidator(
    ValidationPolicy.DISCARD, 
    allow_numbers=True,
    allow_punctuation=False,
    allow_whitespaces=False,
    allow_latin_letters_lowercase=True,
    allow_latin_letters_uppercase=True,
    allow_russian_letters_lowercase=True,
    allow_russian_letters_uppercase=True,
    allow_additionally=' '
)

IntValidator = IntegerValidator(
    ValidationPolicy.DISCARD
)

EnumValidator = EnumerationValidator(
    ValidationPolicy.DISCARD
)

DtValidator = DatetimeValidator(
    ValidationPolicy.DISCARD
)

