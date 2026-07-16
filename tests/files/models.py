import datetime
import datetime as dt
import decimal
import uuid
from typing import Literal, TypedDict

from sqlalchemy import String,  func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class BaseModel(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, nullable=False, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

class SubscriptionPlan(BaseModel):
    __tablename__ = "pt_subscription_plans"



class Subscription(BaseModel):
    __tablename__ = "pt_subscriptions"



class AuthRight(TypedDict):
    section: str
    levels: list[Literal["read", "write", "delete"]]


class Auth(BaseModel):
    __tablename__ = "pt_auths"

class User(BaseModel):
    __tablename__ = "pt_users"


class Profile(BaseModel):
    __tablename__ = "pt_profiles"



class Taking(BaseModel):
    __tablename__ = "pt_takings"



class Supplement(BaseModel):
    __tablename__ = "pt_supplements"


class UserProfileSupplement(BaseModel):
    __tablename__ = "pt_user_profile_supplements"


class MuscleGroup(BaseModel):
    __tablename__ = "pt_muscle_groups"


class Exercise(BaseModel):
    __tablename__ = "pt_exercises"


class DiaryLimit(BaseModel):
    __tablename__ = "pt_diaries"


class UserDiaryLimit(BaseModel):
    __tablename__ = "pt_user_diaries"



class UserTracking(BaseModel):
    __tablename__ = "pt_user_trackings"


class TrackerPhysique(BaseModel):
    __tablename__ = "pt_tracker_physiques"


class TrackerNutrition(BaseModel):
    __tablename__ = "pt_tracker_nutritions"



class TrackerNutritionVegetables(BaseModel):
    __tablename__ = "pt_tracker_nutrition_vegetables"


class TrackerDigestion(BaseModel):
    __tablename__ = "pt_tracker_digestions"


class TrackerSleep(BaseModel):
    __tablename__ = "pt_tracker_sleeps"


class TrackerActivity(BaseModel):
    __tablename__ = "pt_tracker_activities"


class TrackerNote(BaseModel):
    __tablename__ = "pt_tracker_notes"


class Diary:
    fat: Mapped[int] = mapped_column(nullable=True)
    protein: Mapped[int] = mapped_column(nullable=True)
    carbohydrates: Mapped[int] = mapped_column(nullable=True)
    kcal: Mapped[int] = mapped_column(nullable=True)
    standard_weight: Mapped[float] = mapped_column(nullable=True)
    standard_unit: Mapped[str] = mapped_column(String(10), nullable=True)


class DiaryCarbohydrates(BaseModel, Diary):
    __tablename__ = "pt_diary_carbohydrates"


class DiaryProtein(BaseModel, Diary):
    __tablename__ = "pt_diary_protein"


class DiaryFat(BaseModel, Diary):
    __tablename__ = "pt_diary_fat"


class DiaryVegetables(BaseModel, Diary):
    __tablename__ = "pt_diary_vegetables"


class UserNutritionPlan(BaseModel):
    __tablename__ = "pt_user_nutrition_plans"



class TrainingPlan(BaseModel):
    __tablename__ = "pt_training_plans"


class TrainingPlanExercise(BaseModel):
    __tablename__ = "pt_training_plan_exercises"

class UserTrainingExercisePerformance(BaseModel):
    __tablename__ = "pt_user_training_exercise_performances"

class UserTrainingPlanExercise(BaseModel):
    __tablename__ = "pt_user_training_plan_exercises"


class UserTrainingPlan(BaseModel):
    __tablename__ = "pt_user_training_plans"


class UserTrainingExercise(BaseModel):
    __tablename__ = "pt_user_training_exercises"


class UserTraining(BaseModel):
    __tablename__ = "pt_user_trainings"


class Token(BaseModel):
    __tablename__ = "pt_tokens"
