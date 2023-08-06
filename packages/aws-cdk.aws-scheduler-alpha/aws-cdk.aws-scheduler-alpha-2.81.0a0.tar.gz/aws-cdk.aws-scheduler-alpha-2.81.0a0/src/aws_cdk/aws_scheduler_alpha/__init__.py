'''
# Amazon EventBridge Scheduler Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

[Amazon EventBridge Scheduler](https://aws.amazon.com/blogs/compute/introducing-amazon-eventbridge-scheduler/) is a feature from Amazon EventBridge
that allows you to create, run, and manage scheduled tasks at scale. With EventBridge Scheduler, you can schedule one-time or recurrently tens
of millions of tasks across many AWS services without provisioning or managing underlying infrastructure.

1. **Schedule**: A schedule is the main resource you create, configure, and manage using Amazon EventBridge Scheduler. Every schedule has a schedule expression that determines when, and with what frequency, the schedule runs. EventBridge Scheduler supports three types of schedules: rate, cron, and one-time schedules. When you create a schedule, you configure a target for the schedule to invoke.
2. **Targets**: A target is an API operation that EventBridge Scheduler calls on your behalf every time your schedule runs. EventBridge Scheduler
   supports two types of targets: templated targets and universal targets. Templated targets invoke common API operations across a core groups of
   services. For example, EventBridge Scheduler supports templated targets for invoking AWS Lambda Function or starting execution of Step Function state
   machine. For API operations that are not supported by templated targets you can use customizeable universal targets. Universal targets support calling
   more than 6,000 API operations across over 270 AWS services.
3. **Schedule Group**: A schedule group is an Amazon EventBridge Scheduler resource that you use to organize your schedules. Your AWS account comes
   with a default scheduler group. A new schedule will always be added to a scheduling group. If you do not provide a scheduling group to add to, it
   will be added to the default scheduling group. You can create up to 500 schedule groups in your AWS account. Groups can be used to organize the
   schedules logically, access the schedule metrics and manage permissions at group granularity (see details below). Scheduling groups support tagging:
   with EventBridge Scheduler, you apply tags to schedule groups, not to individual schedules to organize your resources.

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project. It allows you to define Event Bridge Schedules.

> This module is in active development. Some features may not be implemented yet.

## Defining a schedule

TODO: Schedule is not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)

### Schedule Expressions

You can choose from three schedule types when configuring your schedule: rate-based, cron-based, and one-time schedules.

Both rate-based and cron-based schedules are recurring schedules. You can configure each recurring schedule type using a schedule expression. For
cron-based schedule you can specify a time zone in which EventBridge Scheduler evaluates the expression.

> ScheduleExpression should be used together with class Schedule, which is not yet implemented.

```text
const rateBasedSchedule = new Schedule(this, 'Schedule', {
    scheduleExpression: ScheduleExpression.rate(Duration.minutes(10)),
    target,
    description: 'This is a test rate-based schedule',
});

const cronBasedSchedule = new Schedule(this, 'Schedule', {
    scheduleExpression: ScheduleExpression.cron({
        minute: '0',
        hour: '23',
        day: '20',
        month: '11',
        timeZone: TimeZone.AMERICA_NEW_YORK,
    }),
    target,
    description: 'This is a test cron-based schedule that will run at 11:00 PM, on day 20 of the month, only in November in New York timezone',
});
```

A one-time schedule is a schedule that invokes a target only once. You configure a one-time schedule when by specifying the time of the day, date,
and time zone in which EventBridge Scheduler evaluates the schedule.

```text
const oneTimeSchedule = new Schedule(this, 'Schedule', {
    scheduleExpression: ScheduleExpression.at(
        new Date(2022, 10, 20, 19, 20, 23),
        TimeZone.AMERICA_NEW_YORK,
    ),
    target,
    description: 'This is a one-time schedule in New York timezone',
});
```

### Grouping Schedules

TODO: Group is not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)

## Scheduler Targets

TODO: Scheduler Targets Module is not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)

### Input

TODO: Target Input is not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)

### Specifying Execution Role

TODO: Not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)

### Cross-account and cross-region targets

Executing cross-account and cross-region targets are not supported yet.

### Specifying Encryption key

TODO: Not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)

## Error-handling

TODO: Not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)

## Overriding Target Properties

TODO: Not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)

## Monitoring

You can monitor Amazon EventBridge Scheduler using CloudWatch, which collects raw data
and processes it into readable, near real-time metrics. EventBridge Scheduler emits
a set of metrics for all schedules, and an additional set of metrics for schedules that
have an associated dead-letter queue (DLQ). If you configure a DLQ for your schedule,
EventBridge Scheduler publishes additional metrics when your schedule exhausts its retry policy.

### Metrics for all schedules

TODO: Not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)

### Metrics for a Group

TODO: Not yet implemented. See section in [L2 Event Bridge Scheduler RFC](https://github.com/aws/aws-cdk-rfcs/blob/master/text/0474-event-bridge-scheduler-l2.md)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d


@jsii.data_type(
    jsii_type="@aws-cdk/aws-scheduler-alpha.CronOptionsWithTimezone",
    jsii_struct_bases=[_aws_cdk_aws_events_ceddda9d.CronOptions],
    name_mapping={
        "day": "day",
        "hour": "hour",
        "minute": "minute",
        "month": "month",
        "week_day": "weekDay",
        "year": "year",
        "time_zone": "timeZone",
    },
)
class CronOptionsWithTimezone(_aws_cdk_aws_events_ceddda9d.CronOptions):
    def __init__(
        self,
        *,
        day: typing.Optional[builtins.str] = None,
        hour: typing.Optional[builtins.str] = None,
        minute: typing.Optional[builtins.str] = None,
        month: typing.Optional[builtins.str] = None,
        week_day: typing.Optional[builtins.str] = None,
        year: typing.Optional[builtins.str] = None,
        time_zone: typing.Optional[_aws_cdk_ceddda9d.TimeZone] = None,
    ) -> None:
        '''(experimental) Options to configure a cron expression.

        All fields are strings so you can use complex expressions. Absence of
        a field implies '*' or '?', whichever one is appropriate.

        :param day: The day of the month to run this rule at. Default: - Every day of the month
        :param hour: The hour to run this rule at. Default: - Every hour
        :param minute: The minute to run this rule at. Default: - Every minute
        :param month: The month to run this rule at. Default: - Every month
        :param week_day: The day of the week to run this rule at. Default: - Any day of the week
        :param year: The year to run this rule at. Default: - Every year
        :param time_zone: (experimental) The timezone to run the schedule in. Default: - TimeZone.ETC_UTC

        :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/scheduled-events.html#cron-expressions
        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_scheduler_alpha as scheduler_alpha
            import aws_cdk as cdk
            
            # time_zone: cdk.TimeZone
            
            cron_options_with_timezone = scheduler_alpha.CronOptionsWithTimezone(
                day="day",
                hour="hour",
                minute="minute",
                month="month",
                time_zone=time_zone,
                week_day="weekDay",
                year="year"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b93c2b718a23f23063cb14b1618a13104c926d0bdf7230ce719160d882d285a)
            check_type(argname="argument day", value=day, expected_type=type_hints["day"])
            check_type(argname="argument hour", value=hour, expected_type=type_hints["hour"])
            check_type(argname="argument minute", value=minute, expected_type=type_hints["minute"])
            check_type(argname="argument month", value=month, expected_type=type_hints["month"])
            check_type(argname="argument week_day", value=week_day, expected_type=type_hints["week_day"])
            check_type(argname="argument year", value=year, expected_type=type_hints["year"])
            check_type(argname="argument time_zone", value=time_zone, expected_type=type_hints["time_zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if day is not None:
            self._values["day"] = day
        if hour is not None:
            self._values["hour"] = hour
        if minute is not None:
            self._values["minute"] = minute
        if month is not None:
            self._values["month"] = month
        if week_day is not None:
            self._values["week_day"] = week_day
        if year is not None:
            self._values["year"] = year
        if time_zone is not None:
            self._values["time_zone"] = time_zone

    @builtins.property
    def day(self) -> typing.Optional[builtins.str]:
        '''The day of the month to run this rule at.

        :default: - Every day of the month
        '''
        result = self._values.get("day")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hour(self) -> typing.Optional[builtins.str]:
        '''The hour to run this rule at.

        :default: - Every hour
        '''
        result = self._values.get("hour")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minute(self) -> typing.Optional[builtins.str]:
        '''The minute to run this rule at.

        :default: - Every minute
        '''
        result = self._values.get("minute")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def month(self) -> typing.Optional[builtins.str]:
        '''The month to run this rule at.

        :default: - Every month
        '''
        result = self._values.get("month")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def week_day(self) -> typing.Optional[builtins.str]:
        '''The day of the week to run this rule at.

        :default: - Any day of the week
        '''
        result = self._values.get("week_day")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def year(self) -> typing.Optional[builtins.str]:
        '''The year to run this rule at.

        :default: - Every year
        '''
        result = self._values.get("year")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[_aws_cdk_ceddda9d.TimeZone]:
        '''(experimental) The timezone to run the schedule in.

        :default: - TimeZone.ETC_UTC

        :stability: experimental
        '''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.TimeZone], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CronOptionsWithTimezone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ScheduleExpression(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-scheduler-alpha.ScheduleExpression",
):
    '''(experimental) ScheduleExpression for EventBridge Schedule.

    You can choose from three schedule types when configuring your schedule: rate-based, cron-based, and one-time schedules.
    Both rate-based and cron-based schedules are recurring schedules.

    :see: https://docs.aws.amazon.com/scheduler/latest/UserGuide/schedule-types.html
    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_scheduler_alpha as scheduler_alpha
        import aws_cdk as cdk
        
        # time_zone: cdk.TimeZone
        
        schedule_expression = scheduler_alpha.ScheduleExpression.at(Date(), time_zone)
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="at")
    @builtins.classmethod
    def at(
        cls,
        date: datetime.datetime,
        time_zone: typing.Optional[_aws_cdk_ceddda9d.TimeZone] = None,
    ) -> "ScheduleExpression":
        '''(experimental) Construct a one-time schedule from a date.

        :param date: The date and time to use. The millisecond part will be ignored.
        :param time_zone: The time zone to use for interpreting the date. Default: - UTC

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bf0285b6946b1db006663f64ebff2eb43720129f53e712d42b59f3d29620873)
            check_type(argname="argument date", value=date, expected_type=type_hints["date"])
            check_type(argname="argument time_zone", value=time_zone, expected_type=type_hints["time_zone"])
        return typing.cast("ScheduleExpression", jsii.sinvoke(cls, "at", [date, time_zone]))

    @jsii.member(jsii_name="cron")
    @builtins.classmethod
    def cron(
        cls,
        *,
        time_zone: typing.Optional[_aws_cdk_ceddda9d.TimeZone] = None,
        day: typing.Optional[builtins.str] = None,
        hour: typing.Optional[builtins.str] = None,
        minute: typing.Optional[builtins.str] = None,
        month: typing.Optional[builtins.str] = None,
        week_day: typing.Optional[builtins.str] = None,
        year: typing.Optional[builtins.str] = None,
    ) -> "ScheduleExpression":
        '''(experimental) Create a recurring schedule from a set of cron fields and time zone.

        :param time_zone: (experimental) The timezone to run the schedule in. Default: - TimeZone.ETC_UTC
        :param day: The day of the month to run this rule at. Default: - Every day of the month
        :param hour: The hour to run this rule at. Default: - Every hour
        :param minute: The minute to run this rule at. Default: - Every minute
        :param month: The month to run this rule at. Default: - Every month
        :param week_day: The day of the week to run this rule at. Default: - Any day of the week
        :param year: The year to run this rule at. Default: - Every year

        :stability: experimental
        '''
        options = CronOptionsWithTimezone(
            time_zone=time_zone,
            day=day,
            hour=hour,
            minute=minute,
            month=month,
            week_day=week_day,
            year=year,
        )

        return typing.cast("ScheduleExpression", jsii.sinvoke(cls, "cron", [options]))

    @jsii.member(jsii_name="expression")
    @builtins.classmethod
    def expression(
        cls,
        expression: builtins.str,
        time_zone: typing.Optional[_aws_cdk_ceddda9d.TimeZone] = None,
    ) -> "ScheduleExpression":
        '''(experimental) Construct a schedule from a literal schedule expression.

        :param expression: The expression to use. Must be in a format that EventBridge will recognize
        :param time_zone: The time zone to use for interpreting the expression. Default: - UTC

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0634c4b66b6d96653bcec6e5c37e7587eb5123a94680df0694878cb2276e874)
            check_type(argname="argument expression", value=expression, expected_type=type_hints["expression"])
            check_type(argname="argument time_zone", value=time_zone, expected_type=type_hints["time_zone"])
        return typing.cast("ScheduleExpression", jsii.sinvoke(cls, "expression", [expression, time_zone]))

    @jsii.member(jsii_name="rate")
    @builtins.classmethod
    def rate(cls, duration: _aws_cdk_ceddda9d.Duration) -> "ScheduleExpression":
        '''(experimental) Construct a recurring schedule from an interval and a time unit.

        Rates may be defined with any unit of time, but when converted into minutes, the duration must be a positive whole number of minutes.

        :param duration: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2f7ba7d57267bb20d2ff8fd156c360c31850c2fb0387099338165ebc5ba04a4)
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
        return typing.cast("ScheduleExpression", jsii.sinvoke(cls, "rate", [duration]))

    @builtins.property
    @jsii.member(jsii_name="expressionString")
    @abc.abstractmethod
    def expression_string(self) -> builtins.str:
        '''(experimental) Retrieve the expression for this schedule.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="timeZone")
    @abc.abstractmethod
    def time_zone(self) -> typing.Optional[_aws_cdk_ceddda9d.TimeZone]:
        '''(experimental) Retrieve the expression for this schedule.

        :stability: experimental
        '''
        ...


class _ScheduleExpressionProxy(ScheduleExpression):
    @builtins.property
    @jsii.member(jsii_name="expressionString")
    def expression_string(self) -> builtins.str:
        '''(experimental) Retrieve the expression for this schedule.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "expressionString"))

    @builtins.property
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> typing.Optional[_aws_cdk_ceddda9d.TimeZone]:
        '''(experimental) Retrieve the expression for this schedule.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.TimeZone], jsii.get(self, "timeZone"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ScheduleExpression).__jsii_proxy_class__ = lambda : _ScheduleExpressionProxy


__all__ = [
    "CronOptionsWithTimezone",
    "ScheduleExpression",
]

publication.publish()

def _typecheckingstub__2b93c2b718a23f23063cb14b1618a13104c926d0bdf7230ce719160d882d285a(
    *,
    day: typing.Optional[builtins.str] = None,
    hour: typing.Optional[builtins.str] = None,
    minute: typing.Optional[builtins.str] = None,
    month: typing.Optional[builtins.str] = None,
    week_day: typing.Optional[builtins.str] = None,
    year: typing.Optional[builtins.str] = None,
    time_zone: typing.Optional[_aws_cdk_ceddda9d.TimeZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bf0285b6946b1db006663f64ebff2eb43720129f53e712d42b59f3d29620873(
    date: datetime.datetime,
    time_zone: typing.Optional[_aws_cdk_ceddda9d.TimeZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0634c4b66b6d96653bcec6e5c37e7587eb5123a94680df0694878cb2276e874(
    expression: builtins.str,
    time_zone: typing.Optional[_aws_cdk_ceddda9d.TimeZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f7ba7d57267bb20d2ff8fd156c360c31850c2fb0387099338165ebc5ba04a4(
    duration: _aws_cdk_ceddda9d.Duration,
) -> None:
    """Type checking stubs"""
    pass
