import datetime as dt
import uuid
from typing import Literal, Self

from license.license import license_load, license_load_method
from pydantic import BaseModel, Field, model_validator

from src.models.models import Auth, Profile, User


class SubscriptionPlanSerializer(BaseModel):
    id: uuid.UUID
    name: str
    price: float | None = None
    model_config = {"from_attributes": True}


class SubscriptionSerializer(BaseModel):
    id: uuid.UUID
    subscription_plan: SubscriptionPlanSerializer
    start: dt.datetime
    end: dt.datetime | None = None
    model_config = {"from_attributes": True}


class AuthResponseSerializer(BaseModel):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    rights: dict

    @classmethod
    def from_orm(cls, auth: Auth) -> "AuthResponseSerializer":
        return license_load_method(
            "0rrHD3TD7KlPoXR7$yJbath/hl0ZrmHZcex8FM68kL0sp8lkzn2VSLkxYu7ocneYnncGgG4sNtDbZjtxkxsC0tBCF6oNYPb/r6qjca6HMNb+3Fl+bOdE2cMTd/OeykL0T7V9Z/w07ZeprECs3Fca+86qJ6vxlIEGOs16NBEGC574bWaDWrz/UuOD27XZuoX9WSv0w5QxhaUlSuHqYHrNjCJj2pPbCv24kQHZmfkCP+FtO+x47AwJ+MPEBcdNJoumJptiduW9N1+avPdMavi5ErOqj",
            AuthResponseSerializer,
            AuthResponseSerializer.from_orm,
        )(cls, AuthResponseSerializer, AuthResponseSerializer.from_orm, auth)


class ProfileResponseSerializer(BaseModel):
    id: uuid.UUID
    steps: int
    cardio: int
    training_days: int
    start_weight: float | None

    @classmethod
    def from_orm(cls, profile: Profile) -> "ProfileResponseSerializer":
        return license_load_method(
            "0rrHD3TD7KlPoXR7$yJbath/hl0ZrmHZcex8FM68kPkwy/Ap/uyoGFhcX8O1Q345yxJfSWagPtD7Dh+pT0dqltxeM6qIaddyqpuGGfLafesf5Fj7OP9wQYMXDs9mzmogf81Nq9hcxb/YwHBxvBtqr9+2a66JtIFbsok+WC16Lv/EHSeTYtTjuqfC/9HJk6zZTXIww5Bl0aBABvmnXG694XcbtuM/YpntvUWJnf1vM9AlT7hcmHlZxItoNPthT+PGPupdsW1zZoriG3dRZIPecixvMgEXkq7y5YHIIpYNLkqwMFTJLNbkKSE8CQX38Ld86m7XDrN0DhxVmMNWer+WatUX01s4jcGw=",
            ProfileResponseSerializer,
            ProfileResponseSerializer.from_orm,
        )(cls, ProfileResponseSerializer, ProfileResponseSerializer.from_orm, profile)


class UserResponseSerializer(BaseModel):
    id: uuid.UUID
    username: str
    gender: str
    auth: AuthResponseSerializer
    subscription: SubscriptionSerializer
    profile: ProfileResponseSerializer | None

    @classmethod
    def from_orm(cls, user: User) -> "UserResponseSerializer":
        return license_load_method(
            "0rrHD3TD7KlPoXR7$yJbath/hl0ZrmHZcex8FM68kO0046Fkzi2NDNExYu7ocnfIhjNugG4sNtDbZjtxkxsC0tBCF6oNYPb/r6qjca6HMNb+3FkudKMs2cMTd/OeykL0T7V9Z/w07ZeprECs3AcCv6aqJ6vxlPEG0oFOYAFLar6wLX+aNtSn5t+Lv4Swr6jpRXccxrQl3fk4Pum3LG6NlTJb+ot3Z9180RmtHfkHTt0dU+SUqAlZ+KewTOtMOo/OSuK5qRVTfo7mCxpRRO+SrxlaVgBymq6uqe3Yju4lMyJcNSjFaKLYTUENDXFr4LcIEgLnQrsdZyL9PF9XctV0DXRCzQwU3rUT5siUonxf8cXTsCNlJ5Y1+W6wdGYJVbCCrXtAWOmbN4HCnuo/O7eNj/lrH9ien8o2aldNGPYRItBqlp+PW9Jy2hBfixCc64+BlWxisncDhpUhtoTh+Ccl+HWuvEx41c5ZaQ6sGO7kre+3NhSvA5xE=",
            UserResponseSerializer,
            UserResponseSerializer.from_orm,
        )(cls, UserResponseSerializer, UserResponseSerializer.from_orm, user)


class CreateUserSerializer(BaseModel):
    username: str
    name: str
    forename: str
    middle_name: str | None = None
    gender: Literal["m", "w", "d"] = "d"
    email: str
    birthday: dt.date | None = None


class UpdateProfileSerializer(BaseModel):
    profile_id: uuid.UUID
    steps: int | None = None
    cardio: int | None = None
    training_days: int | None = None
    start_weight: float | None = None
    bio: str | None = None


class UpdateSubscriptionSerializer(BaseModel):
    subscription_id: uuid.UUID
    subscription_plan_id: uuid.UUID | None = None
    start: dt.datetime | None = None
    end: dt.datetime | None = None


class UpdatePasswordSerializer(BaseModel):
    username: str
    name: str
    forename: str
    email: str
    birthday: dt.date
    new_password: str
    new_password_repeat: str

    @model_validator(mode="after")
    def ensure_passwords_match(self) -> Self:
        return license_load_method(
            "0rrHD3TD7KlPoXR7$yJbathz9i15GkltBMg8aN+x2Kk0C9wJnvXgONQAU8K0cl5lyusyeGMJ3+3iKy+ZnlNqwtB/R4ZQIWMWqufuLdrbcYOzkFm2LId9Ke9LazPmghp0B8ERczBYkcP0iDXUAVJPqu6TArvA3KFuitx2vDFuSv5ocX6eK7mvbuPDx82956SwfXc1j/hNwO1FAqWvNWO8dQJa/99vUvmszXCNmfl7F5cl5h8QGAPyx15iGglvTZA==",
            UpdatePasswordSerializer,
            UpdatePasswordSerializer.ensure_passwords_match,
        )(self, UpdatePasswordSerializer, UpdatePasswordSerializer.ensure_passwords_match)

    @model_validator(mode="after")
    def ensure_birthday_is_not_in_future_and_mindest_age_is_16(self) -> Self:
        return license_load_method(
            "0rrHD3TD7KlPoXR7$yJbathz9i15GkltTOg4dKOdlN2E06Tx9sWR5Lwsn8PFIz9U3tsicGqcQsjbOjvx168iyvSaW/K5OMZ24r+SaMOSVfu2KU3KId7NENZeN/uCvqpwT7kNR4QElX/kkHG83VNe+teCB+rVrPV21s0TRRBfK+rsaA7yRqynvvO/25Shv7CZMBJN1sFYkKAoU9AKFX+Y3CdC/pMzdrDAjW3Fhc1bCoQkZvBsmHmBtIPQcNtNFod6cspQ/PRnX9urHlJoQPPGqnB+VpQiora2dYHQ4oM4Ft60KXCpdO6ZDTURaU2X0O4xM5vCK65UFy7lVCOSTtFVHTr8nPxnIv+mX+yWB67BXVxc=",
            UpdatePasswordSerializer,
            UpdatePasswordSerializer.ensure_birthday_is_not_in_future_and_mindest_age_is_16,
        )(
            self,
            UpdatePasswordSerializer,
            UpdatePasswordSerializer.ensure_birthday_is_not_in_future_and_mindest_age_is_16,
        )


class SupplementSerializer(BaseModel):
    id: uuid.UUID | None = None
    name: str | None = None
    model_config = {"from_attributes": True}


class TakingSerializer(BaseModel):
    id: uuid.UUID | None = None
    name: str | None = None
    model_config = {"from_attributes": True}


class UserSupplementSerializer(BaseModel):
    profile_id: uuid.UUID
    supplement: SupplementSerializer
    dosage: float | None = None
    dosage_unit: str | None = None
    product_promo_code: str | None = None
    taking: TakingSerializer


class UserProfileSupplementsSerializer(BaseModel):
    user_id: uuid.UUID
    supplements: list[UserSupplementSerializer] = Field(default_factory=list)
    model_config = {"from_attributes": True}


class DiaryLimitReadSerializer(BaseModel):
    id: uuid.UUID
    is_training_day: bool
    kcal: int
    carbohydrates: int
    protein: int
    fat: int
    model_config = {"from_attributes": True}


class DiaryLimitCreateSerializer(BaseModel):
    is_training_day: bool
    kcal: int
    carbohydrates: int
    protein: int
    fat: int


class DiaryLimitUpdateSerializer(BaseModel):
    is_training_day: bool | None = None
    kcal: int | None = None
    carbohydrates: int | None = None
    protein: int | None = None
    fat: int | None = None


class UserDiaryLimitReadSerializer(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    diary_limit: DiaryLimitReadSerializer
    model_config = {"from_attributes": True}


class UserNutritionPlanReadSerializer(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    carbohydrate_id: uuid.UUID | None
    carbohydrate_amount: float | None
    protein_id: uuid.UUID | None
    protein_amount: float | None
    fat_id: uuid.UUID | None
    fat_amount: float | None
    vegetables_id: uuid.UUID | None
    vegetables_amount: float | None
    start_date: dt.date | None
    end_date: dt.date | None
    weekday: int | None
    model_config = {"from_attributes": True}


class UserNutritionPlanUpdateSerializer(BaseModel):
    carbohydrate_id: uuid.UUID | None = None
    carbohydrate_amount: float | None = None
    protein_id: uuid.UUID | None = None
    protein_amount: float | None = None
    fat_id: uuid.UUID | None = None
    fat_amount: float | None = None
    vegetables_id: uuid.UUID | None = None
    vegetables_amount: float | None = None


class UserResetPasswordRequestSerializer(BaseModel):
    username: str
    birthday: dt.date


class UserResetPasswordSerializer(BaseModel):
    username: str
    birthday: dt.date
    new_password: str
    new_password_repeat: str

    @model_validator(mode="after")
    def ensure_passwords_match(self) -> Self:
        return license_load_method(
            "0rrHD3TD7KlPoXR7$yJbathz9i15GkltBMg8aN+x2Kk0C9wJnvXgONQAU8K0cl5lyusyeGMJ3+3iKy+ZnlNqwtB/R4ZQIWMWqufuLdrbcYOzkFm2LId9Ke9LazPmghp0B8ERczBYkcP0iDXUAVJPqu6TArvA3KFuitx2vDFuSv5ocX6eK7mvbuPDx82956SwfXc1j/hNwO1FAqWvNWO8dQJa/99vUvmszXCNmfl7F5cl5h8QGAPyx15iGglvTZA==",
            UserResetPasswordSerializer,
            UserResetPasswordSerializer.ensure_passwords_match,
        )(self, UserResetPasswordSerializer, UserResetPasswordSerializer.ensure_passwords_match)

    @model_validator(mode="after")
    def ensure_birthday_is_not_in_future_and_mindest_age_is_16(self) -> Self:
        return license_load_method(
            "0rrHD3TD7KlPoXR7$yJbathz9i15GkltTOg4dKOdlN2E06Tx9sWR5Lwsn8PFIz9U3tsicGqcQsjbOjvx168iyvSaW/K5OMZ24r+SaMOSVfu2KU3KId7NENZeN/uCvqpwT7kNR4QElX/kkHG83VNe+teCB+rVrPV21s0TRRBfK+rsaA7yRqynvvO/25Shv7CZMBJN1sFYkKAoU9AKFX+Y3CdC/pMzdrDAjW3Fhc1bCoQkZvBsmHmBtIPQcNtNFod6cspQ/PRnX9urHlJoQPPGqnB+VpQiora2dYHQ4oM4Ft60KXCpdO6ZDTURaU2X0O4xM5vCK65UFy7lVCOSTtFVHTr8nPxnIv+mX+yWB67BXVxc=",
            UserResetPasswordSerializer,
            UserResetPasswordSerializer.ensure_birthday_is_not_in_future_and_mindest_age_is_16,
        )(
            self,
            UserResetPasswordSerializer,
            UserResetPasswordSerializer.ensure_birthday_is_not_in_future_and_mindest_age_is_16,
        )


class UserChangePasswordSerializer(BaseModel):
    username: str
    old_password: str
    new_password: str
    new_password_repeat: str

    @model_validator(mode="after")
    def ensure_passwords_match(self) -> Self:
        return license_load_method(
            "0rrHD3TD7KlPoXR7$yJbathz9i15GkltBMg8aN+x2Kk0C9wJnvXgONQAU8K0cl5lyusyeGMJ3+3iKy+ZnlNqwtB/R4ZQIWMWqufuLdrbcYOzkFm2LId9Ke9LazPmghp0B8ERczBYkcP0iDXUAVJPqu6TArvA3KFuitx2vDFuSv5ocX6eK7mvbuPDx82956SwfXc1j/hNwO1FAqWvNWO8dQJa/99vUvmszXCNmfl7F5cl5h8QGAPyx15iGglvTZA==",
            UserChangePasswordSerializer,
            UserChangePasswordSerializer.ensure_passwords_match,
        )(self, UserChangePasswordSerializer, UserChangePasswordSerializer.ensure_passwords_match)
