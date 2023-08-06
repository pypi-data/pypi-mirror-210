'''
# cdk-log-notifier: Filter CloudWatch logs and post to Slack.

The AWS CDK Construct to build a system that gather CloudWatch logs, filter and post to Slack.

![screenshot](https://i.imgur.com/Qx2A9n2.png)

## Example Usage

Watch the all logs contains "ERROR" from Lambda functions.

```python
const logNotifier = new LogNotifier(this, 'logNotifier', {
  filterPattern: logs.FilterPattern.allTerms('ERROR'),
  slackIncomingWebhookUrl: 'https://hooks.slack.com/...', // Use yours.
});

logNotifier.watch(lambdaFunc1.logGroup);
logNotifier.watch(lambdaFunc2.logGroup);
```

## Installation

```sh
npm i @thedesignium/cdk-log-notifier
```

## API Reference

### Class: `LogNotifier`

```python
new LogNotifier(scope: cdk.Construct, id: string, props: LogNotifierProps)
```

The properties in `props`:

* `filterPattern`: The [FilterPattern object in aws-cloudwatch module](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.FilterPattern.html). The logs is filtered as specified here. *Required.*
* `slackIncomingWebhookUrl`: The [Incoming Webhook URL](https://api.slack.com/messaging/webhooks) of Slack. Create for the Slack channel the logs should be posted. *Required.*
* `dateTimeFormatOptions`: The [arguments of the DateTimeFormat constructor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat/DateTimeFormat#parameters), used to format the datetime which shown at the bottom of the Slack message. If omitted, it's formatted like `12/20, 3:00:00 AM UTC`. *Optional.*

  Example:

  ```python
    dateTimeFormatOptions: {
      locales: 'ja-JP',
      timeZone: 'Asia/Tokyo',
      month: 'numeric',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      second: 'numeric',
    }
  ```

#### Static Method: `fromAttributes`

```python
LogNotifier.fromAttributes(scope: cdk.Construct, id: string, attrs: LogNotifierAttributes): LogNotifier
```

Instantiate from the attributes. Put the value of `logNotifier.attributes` as `attrs` parameter.

#### Method: `watch`

```python
logNotifier.watch(logGroup: logs.LogGroup): void
```

Add the log group to watch list to notify. The logs in the watched log groups are filtered by the filterPattern and posted to Slack.

#### Property: `attributes`

```python
attributes: LogNotifierAttributes
```

To use with `LogNotifier.fromAttributes()`.

## Containing Resources

* [logs.SubscriptionFilter](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.SubscriptionFilter.html)
* [lambda.Function](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)

## Limitation

The `watch()` method attaches a [Subscription](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Subscriptions.html) to the subject logGroup. The number of subscription can be attached to a logGroup, however, is only one. So it'll fail if the logGroup has another subscription already. Similary, the watched logGroup can't be attached another subscription nor watched from another LogNotifier.

## Motivation

There were 2 requirements:

1. Notice the all logs produced by `console.error()`(not only the crash report such InvocationError)
2. Jump easily to CloudWatch via link

We tried `Lambda's error metric + CloudWatch Alarm + Chatbot` and `CloudWatch Metrics Filter + CloudWatch Alarm + Chatbot`, but the former system don't satisfy [1] and the latter system don't satisfy [2]. That's why we need this.

## FAQ

### Cross Stack?

Possible. Export all values in `LogNotifier.prototype.attributes`, import it and use `LogNotifier.fromAttributes()` in another Stack.

### How can I customize the Slack bot icon or name?

You can set at [Slack App setting page](https://api.slack.com/apps), or Incoming Webhook configuration page if you use [Legacy Incoming Webhook](https://api.slack.com/legacy/custom-integrations/incoming-webhooks).

### No support for other languages than TypeScript?

Supports Python, Java, Go and .NET.
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
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@thedesignium/cdk-log-notifier.DateTimeFormatOptions",
    jsii_struct_bases=[],
    name_mapping={
        "day": "day",
        "era": "era",
        "format_matcher": "formatMatcher",
        "hour": "hour",
        "hour12": "hour12",
        "locale_matcher": "localeMatcher",
        "locales": "locales",
        "minute": "minute",
        "month": "month",
        "second": "second",
        "time_zone": "timeZone",
        "time_zone_name": "timeZoneName",
        "weekday": "weekday",
        "year": "year",
    },
)
class DateTimeFormatOptions:
    def __init__(
        self,
        *,
        day: typing.Optional[builtins.str] = None,
        era: typing.Optional[builtins.str] = None,
        format_matcher: typing.Optional[builtins.str] = None,
        hour: typing.Optional[builtins.str] = None,
        hour12: typing.Optional[builtins.bool] = None,
        locale_matcher: typing.Optional[builtins.str] = None,
        locales: typing.Optional[typing.Union[builtins.str, typing.Sequence[builtins.str]]] = None,
        minute: typing.Optional[builtins.str] = None,
        month: typing.Optional[builtins.str] = None,
        second: typing.Optional[builtins.str] = None,
        time_zone: typing.Optional[builtins.str] = None,
        time_zone_name: typing.Optional[builtins.str] = None,
        weekday: typing.Optional[builtins.str] = None,
        year: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param day: -
        :param era: -
        :param format_matcher: -
        :param hour: -
        :param hour12: -
        :param locale_matcher: -
        :param locales: -
        :param minute: -
        :param month: -
        :param second: -
        :param time_zone: -
        :param time_zone_name: -
        :param weekday: -
        :param year: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bffb6e5772e533ea8e3951cd873e3c29bd11ddf57560eecfff6f8f28443b525a)
            check_type(argname="argument day", value=day, expected_type=type_hints["day"])
            check_type(argname="argument era", value=era, expected_type=type_hints["era"])
            check_type(argname="argument format_matcher", value=format_matcher, expected_type=type_hints["format_matcher"])
            check_type(argname="argument hour", value=hour, expected_type=type_hints["hour"])
            check_type(argname="argument hour12", value=hour12, expected_type=type_hints["hour12"])
            check_type(argname="argument locale_matcher", value=locale_matcher, expected_type=type_hints["locale_matcher"])
            check_type(argname="argument locales", value=locales, expected_type=type_hints["locales"])
            check_type(argname="argument minute", value=minute, expected_type=type_hints["minute"])
            check_type(argname="argument month", value=month, expected_type=type_hints["month"])
            check_type(argname="argument second", value=second, expected_type=type_hints["second"])
            check_type(argname="argument time_zone", value=time_zone, expected_type=type_hints["time_zone"])
            check_type(argname="argument time_zone_name", value=time_zone_name, expected_type=type_hints["time_zone_name"])
            check_type(argname="argument weekday", value=weekday, expected_type=type_hints["weekday"])
            check_type(argname="argument year", value=year, expected_type=type_hints["year"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if day is not None:
            self._values["day"] = day
        if era is not None:
            self._values["era"] = era
        if format_matcher is not None:
            self._values["format_matcher"] = format_matcher
        if hour is not None:
            self._values["hour"] = hour
        if hour12 is not None:
            self._values["hour12"] = hour12
        if locale_matcher is not None:
            self._values["locale_matcher"] = locale_matcher
        if locales is not None:
            self._values["locales"] = locales
        if minute is not None:
            self._values["minute"] = minute
        if month is not None:
            self._values["month"] = month
        if second is not None:
            self._values["second"] = second
        if time_zone is not None:
            self._values["time_zone"] = time_zone
        if time_zone_name is not None:
            self._values["time_zone_name"] = time_zone_name
        if weekday is not None:
            self._values["weekday"] = weekday
        if year is not None:
            self._values["year"] = year

    @builtins.property
    def day(self) -> typing.Optional[builtins.str]:
        result = self._values.get("day")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def era(self) -> typing.Optional[builtins.str]:
        result = self._values.get("era")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def format_matcher(self) -> typing.Optional[builtins.str]:
        result = self._values.get("format_matcher")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hour(self) -> typing.Optional[builtins.str]:
        result = self._values.get("hour")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hour12(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("hour12")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def locale_matcher(self) -> typing.Optional[builtins.str]:
        result = self._values.get("locale_matcher")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locales(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, typing.List[builtins.str]]]:
        result = self._values.get("locales")
        return typing.cast(typing.Optional[typing.Union[builtins.str, typing.List[builtins.str]]], result)

    @builtins.property
    def minute(self) -> typing.Optional[builtins.str]:
        result = self._values.get("minute")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def month(self) -> typing.Optional[builtins.str]:
        result = self._values.get("month")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def second(self) -> typing.Optional[builtins.str]:
        result = self._values.get("second")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[builtins.str]:
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_zone_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("time_zone_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def weekday(self) -> typing.Optional[builtins.str]:
        result = self._values.get("weekday")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def year(self) -> typing.Optional[builtins.str]:
        result = self._values.get("year")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DateTimeFormatOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@thedesignium/cdk-log-notifier.ILogNotifier")
class ILogNotifier(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="destinationFunctionArn")
    def destination_function_arn(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="filterPattern")
    def filter_pattern(self) -> _aws_cdk_aws_logs_ceddda9d.IFilterPattern:
        ...

    @jsii.member(jsii_name="watch")
    def watch(self, log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup) -> None:
        '''
        :param log_group: -
        '''
        ...


class _ILogNotifierProxy:
    __jsii_type__: typing.ClassVar[str] = "@thedesignium/cdk-log-notifier.ILogNotifier"

    @builtins.property
    @jsii.member(jsii_name="destinationFunctionArn")
    def destination_function_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationFunctionArn"))

    @builtins.property
    @jsii.member(jsii_name="filterPattern")
    def filter_pattern(self) -> _aws_cdk_aws_logs_ceddda9d.IFilterPattern:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.IFilterPattern, jsii.get(self, "filterPattern"))

    @jsii.member(jsii_name="watch")
    def watch(self, log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup) -> None:
        '''
        :param log_group: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6c1792d6d7979581f0572e192b4d15c353d930fe374a3f5dd10e7680c95bf20)
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
        return typing.cast(None, jsii.invoke(self, "watch", [log_group]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILogNotifier).__jsii_proxy_class__ = lambda : _ILogNotifierProxy


@jsii.implements(ILogNotifier)
class LogNotifier(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@thedesignium/cdk-log-notifier.LogNotifier",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        filter_pattern: _aws_cdk_aws_logs_ceddda9d.IFilterPattern,
        slack_incoming_webhook_url: builtins.str,
        date_time_format_options: typing.Optional[typing.Union[DateTimeFormatOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param filter_pattern: -
        :param slack_incoming_webhook_url: -
        :param date_time_format_options: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0096fbf23a094fb05a9b3d2cf3817eef0052ed67e29480a0f45ab38595b7963d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LogNotifierProps(
            filter_pattern=filter_pattern,
            slack_incoming_webhook_url=slack_incoming_webhook_url,
            date_time_format_options=date_time_format_options,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAttributes")
    @builtins.classmethod
    def from_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        destination_function_arn: builtins.str,
        filter_pattern: _aws_cdk_aws_logs_ceddda9d.IFilterPattern,
    ) -> ILogNotifier:
        '''
        :param scope: -
        :param id: -
        :param destination_function_arn: -
        :param filter_pattern: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43fb2d741f81fdc18f2595e7621f8515e190c649521a35afa0b9e4d9e65f9c3b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = LogNotifierAttributes(
            destination_function_arn=destination_function_arn,
            filter_pattern=filter_pattern,
        )

        return typing.cast(ILogNotifier, jsii.sinvoke(cls, "fromAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="watch")
    def watch(self, log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup) -> None:
        '''
        :param log_group: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b39e83aa0036e913b45c6be5dc00de0fb39364571c3fd55bab0fa52f05c2b8a7)
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
        return typing.cast(None, jsii.invoke(self, "watch", [log_group]))

    @builtins.property
    @jsii.member(jsii_name="attributes")
    def attributes(self) -> "LogNotifierAttributes":
        return typing.cast("LogNotifierAttributes", jsii.get(self, "attributes"))

    @builtins.property
    @jsii.member(jsii_name="destinationFunctionArn")
    def destination_function_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationFunctionArn"))

    @builtins.property
    @jsii.member(jsii_name="filterPattern")
    def filter_pattern(self) -> _aws_cdk_aws_logs_ceddda9d.IFilterPattern:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.IFilterPattern, jsii.get(self, "filterPattern"))

    @builtins.property
    @jsii.member(jsii_name="handleLogFunc")
    def _handle_log_func(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "handleLogFunc"))

    @_handle_log_func.setter
    def _handle_log_func(self, value: _aws_cdk_aws_lambda_ceddda9d.IFunction) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1031b1403822bc9ccd4196d48703f3e59098a540ab2f8afef6b31a9da52d63a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "handleLogFunc", value)


@jsii.data_type(
    jsii_type="@thedesignium/cdk-log-notifier.LogNotifierAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "destination_function_arn": "destinationFunctionArn",
        "filter_pattern": "filterPattern",
    },
)
class LogNotifierAttributes:
    def __init__(
        self,
        *,
        destination_function_arn: builtins.str,
        filter_pattern: _aws_cdk_aws_logs_ceddda9d.IFilterPattern,
    ) -> None:
        '''
        :param destination_function_arn: -
        :param filter_pattern: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c601fa7b9bb56f8dfb1e31c0dcf6d0452e1b75fdfe4a7e9e1dd805f6050da04d)
            check_type(argname="argument destination_function_arn", value=destination_function_arn, expected_type=type_hints["destination_function_arn"])
            check_type(argname="argument filter_pattern", value=filter_pattern, expected_type=type_hints["filter_pattern"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination_function_arn": destination_function_arn,
            "filter_pattern": filter_pattern,
        }

    @builtins.property
    def destination_function_arn(self) -> builtins.str:
        result = self._values.get("destination_function_arn")
        assert result is not None, "Required property 'destination_function_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter_pattern(self) -> _aws_cdk_aws_logs_ceddda9d.IFilterPattern:
        result = self._values.get("filter_pattern")
        assert result is not None, "Required property 'filter_pattern' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.IFilterPattern, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogNotifierAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@thedesignium/cdk-log-notifier.LogNotifierProps",
    jsii_struct_bases=[],
    name_mapping={
        "filter_pattern": "filterPattern",
        "slack_incoming_webhook_url": "slackIncomingWebhookUrl",
        "date_time_format_options": "dateTimeFormatOptions",
    },
)
class LogNotifierProps:
    def __init__(
        self,
        *,
        filter_pattern: _aws_cdk_aws_logs_ceddda9d.IFilterPattern,
        slack_incoming_webhook_url: builtins.str,
        date_time_format_options: typing.Optional[typing.Union[DateTimeFormatOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param filter_pattern: -
        :param slack_incoming_webhook_url: -
        :param date_time_format_options: -
        '''
        if isinstance(date_time_format_options, dict):
            date_time_format_options = DateTimeFormatOptions(**date_time_format_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d87e016c1773db7ee8bbe4b7ccdf716b7278b30cd216e29b1d48a4f5b6cbe23)
            check_type(argname="argument filter_pattern", value=filter_pattern, expected_type=type_hints["filter_pattern"])
            check_type(argname="argument slack_incoming_webhook_url", value=slack_incoming_webhook_url, expected_type=type_hints["slack_incoming_webhook_url"])
            check_type(argname="argument date_time_format_options", value=date_time_format_options, expected_type=type_hints["date_time_format_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "filter_pattern": filter_pattern,
            "slack_incoming_webhook_url": slack_incoming_webhook_url,
        }
        if date_time_format_options is not None:
            self._values["date_time_format_options"] = date_time_format_options

    @builtins.property
    def filter_pattern(self) -> _aws_cdk_aws_logs_ceddda9d.IFilterPattern:
        result = self._values.get("filter_pattern")
        assert result is not None, "Required property 'filter_pattern' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.IFilterPattern, result)

    @builtins.property
    def slack_incoming_webhook_url(self) -> builtins.str:
        result = self._values.get("slack_incoming_webhook_url")
        assert result is not None, "Required property 'slack_incoming_webhook_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def date_time_format_options(self) -> typing.Optional[DateTimeFormatOptions]:
        result = self._values.get("date_time_format_options")
        return typing.cast(typing.Optional[DateTimeFormatOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogNotifierProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DateTimeFormatOptions",
    "ILogNotifier",
    "LogNotifier",
    "LogNotifierAttributes",
    "LogNotifierProps",
]

publication.publish()

def _typecheckingstub__bffb6e5772e533ea8e3951cd873e3c29bd11ddf57560eecfff6f8f28443b525a(
    *,
    day: typing.Optional[builtins.str] = None,
    era: typing.Optional[builtins.str] = None,
    format_matcher: typing.Optional[builtins.str] = None,
    hour: typing.Optional[builtins.str] = None,
    hour12: typing.Optional[builtins.bool] = None,
    locale_matcher: typing.Optional[builtins.str] = None,
    locales: typing.Optional[typing.Union[builtins.str, typing.Sequence[builtins.str]]] = None,
    minute: typing.Optional[builtins.str] = None,
    month: typing.Optional[builtins.str] = None,
    second: typing.Optional[builtins.str] = None,
    time_zone: typing.Optional[builtins.str] = None,
    time_zone_name: typing.Optional[builtins.str] = None,
    weekday: typing.Optional[builtins.str] = None,
    year: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6c1792d6d7979581f0572e192b4d15c353d930fe374a3f5dd10e7680c95bf20(
    log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0096fbf23a094fb05a9b3d2cf3817eef0052ed67e29480a0f45ab38595b7963d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    filter_pattern: _aws_cdk_aws_logs_ceddda9d.IFilterPattern,
    slack_incoming_webhook_url: builtins.str,
    date_time_format_options: typing.Optional[typing.Union[DateTimeFormatOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43fb2d741f81fdc18f2595e7621f8515e190c649521a35afa0b9e4d9e65f9c3b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    destination_function_arn: builtins.str,
    filter_pattern: _aws_cdk_aws_logs_ceddda9d.IFilterPattern,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b39e83aa0036e913b45c6be5dc00de0fb39364571c3fd55bab0fa52f05c2b8a7(
    log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1031b1403822bc9ccd4196d48703f3e59098a540ab2f8afef6b31a9da52d63a8(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c601fa7b9bb56f8dfb1e31c0dcf6d0452e1b75fdfe4a7e9e1dd805f6050da04d(
    *,
    destination_function_arn: builtins.str,
    filter_pattern: _aws_cdk_aws_logs_ceddda9d.IFilterPattern,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d87e016c1773db7ee8bbe4b7ccdf716b7278b30cd216e29b1d48a4f5b6cbe23(
    *,
    filter_pattern: _aws_cdk_aws_logs_ceddda9d.IFilterPattern,
    slack_incoming_webhook_url: builtins.str,
    date_time_format_options: typing.Optional[typing.Union[DateTimeFormatOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
