from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from files.models import UserTracking, TrackerNutrition, TrackerActivity, TrackerNutritionVegetables, TrackerPhysique, \
    TrackerDigestion, TrackerSleep, TrackerNote, User, Subscription, Auth, Profile, SubscriptionPlan, Taking, Supplement, \
    UserProfileSupplement, MuscleGroup, Exercise, TrainingPlan, TrainingPlanExercise, DiaryCarbohydrates, DiaryProtein, \
    DiaryFat, DiaryVegetables, UserTrainingPlan, UserTrainingPlanExercise, UserTraining, UserDiaryLimit, \
    UserNutritionPlan, DiaryLimit, Diary, UserTrainingExercisePerformance, Token
from files.serializers.training_serializer import *
from files.serializers.utilities_serializer import *


async def get_training_plans(
    session: AsyncSession,
) -> Sequence[TrainingPlan]:
    stmnt = select(TrainingPlan).options(joinedload(TrainingPlan.exercises), joinedload(TrainingPlan.muscle_group))
    resp = await session.execute(stmnt)
    return resp.unique().scalars().all()


async def get_training_plan(session: AsyncSession, training_plan_id: uuid.UUID) -> TrainingPlan | None:
    stmt = (
        select(TrainingPlan)
        .where(TrainingPlan.id == training_plan_id)
        .options(joinedload(TrainingPlan.exercises), joinedload(TrainingPlan.muscle_group))
    )
    resp = await session.execute(stmt)
    return resp.unique().scalar_one_or_none()


async def update_training_plan(
    session: AsyncSession, training_plan_id: uuid.UUID, data: TrainingPlanUpdateSerializer
) -> TrainingPlan | None:
    stmt = select(TrainingPlan).where(TrainingPlan.id == training_plan_id).options(joinedload(TrainingPlan.exercises))
    resp = await session.execute(stmt)
    training_plan = resp.unique().scalar_one_or_none()
    if not training_plan:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if "exercises" in update_data:
        exercises_ids = update_data.pop("exercises")
        # Clear existing exercises
        training_plan.exercises = []
        # Add new ones
        for exercise_id in exercises_ids:
            training_plan.exercises.append(
                TrainingPlanExercise(training_plan_id=training_plan.id, exercise_id=exercise_id)
            )

    for key, value in update_data.items():
        setattr(training_plan, key, value)

    await session.commit()
    await session.refresh(training_plan, ["exercises", "muscle_group"])
    return training_plan


async def update_exercise_performance(
    session: AsyncSession,
    user_id: uuid.UUID,
    user_training_plan_id: uuid.UUID,
    exercise_id: uuid.UUID,
    data: UserTrainingPerformanceUpdateSerializer,
) -> UserTrainingExercisePerformance | None:
    stmt = await session.execute(
        select(UserTrainingExercisePerformance)
        .where(UserTrainingExercisePerformance.user_id == user_id)
        .where(UserTrainingExercisePerformance.user_training_plan_id == user_training_plan_id)
        .where(UserTrainingExercisePerformance.exercise_id == exercise_id)
        .where(UserTrainingExercisePerformance.set == data.set)
    )
    performance = stmt.scalar_one_or_none()
    if not performance:
        raise SQLAlchemyError("Exercise performance not found")

    for key, value in data.model_dump(exclude_unset=True, exclude={"set"}).items():
        setattr(performance, key, value)
    session.add(performance)
    await session.commit()
    await session.refresh(performance)
    return performance
