import sgqlc.types
import sgqlc.operation
from . import schema

_schema = schema
_schema_root = _schema.schema

__all__ = ('Operations',)


def fragment_coupon_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Coupon, 'CouponFragment')
    _frag.id()
    _frag.discount_value()
    _frag.type()
    _frag.additional_meta_data()
    _frag.ref_id()
    _frag.name()
    _frag.description()
    _frag.created_at()
    _frag.updated_at()
    _frag.billing_id()
    _frag.billing_link_url()
    _frag.type()
    _frag.status()
    _frag_sync_states = _frag.sync_states()
    _frag_sync_states.vendor_identifier()
    _frag_sync_states.status()
    _frag_customers = _frag.customers()
    _frag_customers.id()
    return _frag


def fragment_price_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Price, 'PriceFragment')
    _frag.billing_model()
    _frag.billing_period()
    _frag.billing_id()
    _frag.min_unit_quantity()
    _frag.max_unit_quantity()
    _frag.billing_country_code()
    _frag_price = _frag.price()
    _frag_price.amount()
    _frag_price.currency()
    _frag_feature = _frag.feature()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    return _frag


def fragment_total_price_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerSubscriptionTotalPrice, 'TotalPriceFragment')
    _frag_sub_total = _frag.sub_total()
    _frag_sub_total.amount()
    _frag_sub_total.currency()
    _frag_total = _frag.total()
    _frag_total.amount()
    _frag_total.currency()
    return _frag


def fragment_package_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PackageEntitlement, 'PackageEntitlementFragment')
    _frag.usage_limit()
    _frag.has_unlimited_usage()
    _frag.feature_id()
    _frag.reset_period()
    _frag.hidden_from_widgets()
    _frag.is_custom()
    _frag.display_name_override()
    _frag_feature = _frag.feature()
    _frag_feature.feature_type()
    _frag_feature.meter_type()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    _frag_feature.ref_id()
    _frag_feature.additional_meta_data()
    return _frag


def fragment_addon_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Addon, 'AddonFragment')
    _frag.id()
    _frag.ref_id()
    _frag.billing_id()
    _frag.display_name()
    _frag.description()
    _frag.additional_meta_data()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_package_entitlement_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_price_fragment())
    _frag.pricing_type()
    return _frag


def fragment_plan_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Plan, 'PlanFragment')
    _frag.id()
    _frag.ref_id()
    _frag.display_name()
    _frag.description()
    _frag.billing_id()
    _frag.additional_meta_data()
    _frag_product = _frag.product()
    _frag_product.__fragment__(fragment_product_fragment())
    _frag_base_plan = _frag.base_plan()
    _frag_base_plan.ref_id()
    _frag_base_plan.display_name()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_package_entitlement_fragment())
    _frag_inherited_entitlements = _frag.inherited_entitlements()
    _frag_inherited_entitlements.__fragment__(fragment_package_entitlement_fragment())
    _frag_compatible_addons = _frag.compatible_addons()
    _frag_compatible_addons.__fragment__(fragment_addon_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_price_fragment())
    _frag.pricing_type()
    _frag_default_trial_config = _frag.default_trial_config()
    _frag_default_trial_config.duration()
    _frag_default_trial_config.units()
    return _frag


def fragment_customer_resource_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerResource, 'CustomerResourceFragment')
    _frag.resource_id()
    return _frag


def fragment_slim_subscription_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerSubscription, 'SlimSubscriptionFragment')
    _frag.id()
    _frag.ref_id()
    _frag.status()
    _frag.additional_meta_data()
    _frag.billing_id()
    _frag.billing_link_url()
    _frag.effective_end_date()
    _frag.current_billing_period_end()
    _frag.pricing_type()
    _frag_resource = _frag.resource()
    _frag_resource.__fragment__(fragment_customer_resource_fragment())
    _frag_experiment_info = _frag.experiment_info()
    _frag_experiment_info.name()
    _frag_experiment_info.id()
    _frag_experiment_info.group_name()
    _frag_experiment_info.group_type()
    _frag_prices = _frag.prices()
    _frag_prices.usage_limit()
    _frag_prices_price = _frag_prices.price()
    _frag_prices_price.__fragment__(fragment_price_fragment())
    _frag_total_price = _frag.total_price()
    _frag_total_price.__fragment__(fragment_total_price_fragment())
    _frag_plan = _frag.plan()
    _frag_plan.id()
    _frag_plan.ref_id()
    _frag_addons = _frag.addons()
    _frag_addons.quantity()
    _frag_addons_addon = _frag_addons.addon()
    _frag_addons_addon.id()
    _frag_addons_addon.ref_id()
    _frag_customer = _frag.customer()
    _frag_customer.id()
    _frag_customer.ref_id()
    return _frag


def fragment_subscription_scheduled_update_data():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionScheduledUpdate, 'SubscriptionScheduledUpdateData')
    _frag.subscription_schedule_type()
    _frag.schedule_status()
    _frag.scheduled_execution_time()
    _frag_target_package = _frag.target_package()
    _frag_target_package.id()
    _frag_target_package.ref_id()
    _frag_target_package.display_name()
    _frag_schedule_variables = _frag.schedule_variables()
    _frag_schedule_variables__as__DowngradeChangeVariables = _frag_schedule_variables.__as__(_schema.DowngradeChangeVariables)
    _frag_schedule_variables__as__DowngradeChangeVariables.addon_ref_ids()
    _frag_schedule_variables__as__DowngradeChangeVariables.billing_period()
    _frag_schedule_variables__as__DowngradeChangeVariables.downgrade_plan_ref_id()
    _frag_schedule_variables__as__BillingPeriodChangeVariables = _frag_schedule_variables.__as__(_schema.BillingPeriodChangeVariables)
    _frag_schedule_variables__as__BillingPeriodChangeVariables.billing_period()
    _frag_schedule_variables__as__UnitAmountChangeVariables = _frag_schedule_variables.__as__(_schema.UnitAmountChangeVariables)
    _frag_schedule_variables__as__UnitAmountChangeVariables.new_unit_amount()
    return _frag


def fragment_subscription_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerSubscription, 'SubscriptionFragment')
    _frag.id()
    _frag.start_date()
    _frag.end_date()
    _frag.trial_end_date()
    _frag.cancellation_date()
    _frag.effective_end_date()
    _frag.status()
    _frag.ref_id()
    _frag.current_billing_period_end()
    _frag.additional_meta_data()
    _frag.billing_id()
    _frag.billing_link_url()
    _frag_resource = _frag.resource()
    _frag_resource.__fragment__(fragment_customer_resource_fragment())
    _frag_experiment_info = _frag.experiment_info()
    _frag_experiment_info.name()
    _frag_experiment_info.group_type()
    _frag_experiment_info.group_name()
    _frag_experiment_info.id()
    _frag_prices = _frag.prices()
    _frag_prices.usage_limit()
    _frag_prices_price = _frag_prices.price()
    _frag_prices_price.__fragment__(fragment_price_fragment())
    _frag_total_price = _frag.total_price()
    _frag_total_price.__fragment__(fragment_total_price_fragment())
    _frag.pricing_type()
    _frag_plan = _frag.plan()
    _frag_plan.__fragment__(fragment_plan_fragment())
    _frag_addons = _frag.addons()
    _frag_addons.id()
    _frag_addons.quantity()
    _frag_addons_addon = _frag_addons.addon()
    _frag_addons_addon.__fragment__(fragment_addon_fragment())
    _frag_scheduled_updates = _frag.scheduled_updates()
    _frag_scheduled_updates.__fragment__(fragment_subscription_scheduled_update_data())
    return _frag


def fragment_promotional_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PromotionalEntitlement, 'PromotionalEntitlementFragment')
    _frag.status()
    _frag.usage_limit()
    _frag.feature_id()
    _frag.has_unlimited_usage()
    _frag.reset_period()
    _frag.end_date()
    _frag.is_visible()
    _frag_feature = _frag.feature()
    _frag_feature.feature_type()
    _frag_feature.meter_type()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    _frag_feature.ref_id()
    _frag_feature.additional_meta_data()
    return _frag


def fragment_slim_customer_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Customer, 'SlimCustomerFragment')
    _frag.id()
    _frag.name()
    _frag.email()
    _frag.created_at()
    _frag.updated_at()
    _frag.ref_id()
    _frag.billing_id()
    _frag.additional_meta_data()
    return _frag


def fragment_customer_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Customer, 'CustomerFragment')
    _frag.__fragment__(fragment_slim_customer_fragment())
    _frag.has_payment_method()
    _frag.has_active_subscription()
    _frag.default_payment_expiration_month()
    _frag.default_payment_expiration_year()
    _frag.default_payment_method_last4_digits()
    _frag_trialed_plans = _frag.trialed_plans()
    _frag_trialed_plans.product_id()
    _frag_trialed_plans.product_ref_id()
    _frag_trialed_plans.plan_ref_id()
    _frag_trialed_plans.plan_id()
    _frag_experiment_info = _frag.experiment_info()
    _frag_experiment_info.group_type()
    _frag_experiment_info.group_name()
    _frag_experiment_info.id()
    _frag_experiment_info.name()
    _frag_coupon = _frag.coupon()
    _frag_coupon.__fragment__(fragment_coupon_fragment())
    _frag_eligible_for_trial = _frag.eligible_for_trial()
    _frag_eligible_for_trial.product_id()
    _frag_eligible_for_trial.product_ref_id()
    _frag_eligible_for_trial.eligible()
    _frag_promotional_entitlements = _frag.promotional_entitlements()
    _frag_promotional_entitlements.__fragment__(fragment_promotional_entitlement_fragment())
    return _frag


def fragment_customer_with_subscriptions_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Customer, 'CustomerWithSubscriptionsFragment')
    _frag.__fragment__(fragment_customer_fragment())
    _frag_subscriptions = _frag.subscriptions()
    _frag_subscriptions.__fragment__(fragment_subscription_fragment())
    return _frag


def fragment_subscription_preview_fragment():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionPreview, 'SubscriptionPreviewFragment')
    _frag_sub_total = _frag.sub_total()
    _frag_sub_total.amount()
    _frag_sub_total.currency()
    _frag_total_excluding_tax = _frag.total_excluding_tax()
    _frag_total_excluding_tax.amount()
    _frag_total_excluding_tax.currency()
    _frag_total = _frag.total()
    _frag_total.amount()
    _frag_total.currency()
    _frag_tax_details = _frag.tax_details()
    _frag_tax_details.display_name()
    _frag_tax_details.percentage()
    _frag_tax_details.inclusive()
    _frag_tax = _frag.tax()
    _frag_tax.amount()
    _frag_tax.currency()
    _frag_billing_period_range = _frag.billing_period_range()
    _frag_billing_period_range.start()
    _frag_billing_period_range.end()
    _frag_discount = _frag.discount()
    _frag_discount.type()
    _frag_discount.value()
    _frag_discount.duration_type()
    _frag_discount.duration_in_months()
    _frag_subscription = _frag.subscription()
    _frag_subscription_sub_total = _frag_subscription.sub_total()
    _frag_subscription_sub_total.amount()
    _frag_subscription_sub_total.currency()
    _frag_subscription_total_excluding_tax = _frag_subscription.total_excluding_tax()
    _frag_subscription_total_excluding_tax.amount()
    _frag_subscription_total_excluding_tax.currency()
    _frag_subscription_total = _frag_subscription.total()
    _frag_subscription_total.amount()
    _frag_subscription_total.currency()
    _frag_subscription_tax = _frag_subscription.tax()
    _frag_subscription_tax.amount()
    _frag_subscription_tax.currency()
    _frag_proration = _frag.proration()
    _frag_proration.proration_date()
    _frag_proration_credit = _frag_proration.credit()
    _frag_proration_credit.amount()
    _frag_proration_credit.currency()
    _frag_proration_debit = _frag_proration.debit()
    _frag_proration_debit.amount()
    _frag_proration_debit.currency()
    _frag_proration_net_amount = _frag_proration.net_amount()
    _frag_proration_net_amount.amount()
    _frag_proration_net_amount.currency()
    return _frag


def fragment_feature_fragment():
    _frag = sgqlc.operation.Fragment(_schema.EntitlementFeature, 'FeatureFragment')
    _frag.feature_type()
    _frag.meter_type()
    _frag.feature_units()
    _frag.feature_units_plural()
    _frag.description()
    _frag.display_name()
    _frag.ref_id()
    return _frag


def fragment_reset_period_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.ResetPeriodConfiguration, 'ResetPeriodConfigurationFragment')
    _frag.__typename__()
    _frag__as__MonthlyResetPeriodConfig = _frag.__as__(_schema.MonthlyResetPeriodConfig)
    _frag__as__MonthlyResetPeriodConfig.monthly_according_to()
    _frag__as__WeeklyResetPeriodConfig = _frag.__as__(_schema.WeeklyResetPeriodConfig)
    _frag__as__WeeklyResetPeriodConfig.weekly_according_to()
    return _frag


def fragment_usage_updated_fragment():
    _frag = sgqlc.operation.Fragment(_schema.UsageMeasurementUpdated, 'UsageUpdatedFragment')
    _frag.customer_id()
    _frag.resource_id()
    _frag.feature_id()
    _frag.current_usage()
    _frag.next_reset_date()
    return _frag


def fragment_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Entitlement, 'EntitlementFragment')
    _frag.is_granted()
    _frag.access_denied_reason()
    _frag.customer_id()
    _frag.resource_id()
    _frag.usage_limit()
    _frag.has_unlimited_usage()
    _frag.current_usage()
    _frag.requested_usage()
    _frag.entitlement_updated_at()
    _frag.usage_updated_at()
    _frag.next_reset_date()
    _frag.reset_period()
    _frag_reset_period_configuration = _frag.reset_period_configuration()
    _frag_reset_period_configuration.__fragment__(fragment_reset_period_configuration_fragment())
    _frag_feature = _frag.feature()
    _frag_feature.__fragment__(fragment_feature_fragment())
    return _frag


def fragment_paywall_package_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PackageEntitlement, 'PaywallPackageEntitlementFragment')
    _frag.usage_limit()
    _frag.has_unlimited_usage()
    _frag.feature_id()
    _frag.reset_period()
    _frag.hidden_from_widgets()
    _frag.display_name_override()
    _frag_feature = _frag.feature()
    _frag_feature.feature_type()
    _frag_feature.meter_type()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    _frag_feature.ref_id()
    _frag_feature.additional_meta_data()
    return _frag


def fragment_paywall_addon_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Addon, 'PaywallAddonFragment')
    _frag.id()
    _frag.ref_id()
    _frag.billing_id()
    _frag.display_name()
    _frag.description()
    _frag.additional_meta_data()
    _frag.billing_id()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_paywall_package_entitlement_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_price_fragment())
    _frag.additional_meta_data()
    _frag.pricing_type()
    return _frag


def fragment_paywall_plan_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Plan, 'PaywallPlanFragment')
    _frag.id()
    _frag.ref_id()
    _frag.description()
    _frag.display_name()
    _frag.billing_id()
    _frag_product = _frag.product()
    _frag_product.__fragment__(fragment_product_fragment())
    _frag_base_plan = _frag.base_plan()
    _frag_base_plan.ref_id()
    _frag_base_plan.display_name()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_paywall_package_entitlement_fragment())
    _frag.additional_meta_data()
    _frag_inherited_entitlements = _frag.inherited_entitlements()
    _frag_inherited_entitlements.__fragment__(fragment_paywall_package_entitlement_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_price_fragment())
    _frag.pricing_type()
    _frag_default_trial_config = _frag.default_trial_config()
    _frag_default_trial_config.duration()
    _frag_default_trial_config.units()
    _frag_compatible_addons = _frag.compatible_addons()
    _frag_compatible_addons.__fragment__(fragment_paywall_addon_fragment())
    return _frag


def fragment_typography_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.TypographyConfiguration, 'TypographyConfigurationFragment')
    _frag.font_family()
    _frag_h1 = _frag.h1()
    _frag_h1.__fragment__(fragment_font_variant_fragment())
    _frag_h2 = _frag.h2()
    _frag_h2.__fragment__(fragment_font_variant_fragment())
    _frag_h3 = _frag.h3()
    _frag_h3.__fragment__(fragment_font_variant_fragment())
    _frag_body = _frag.body()
    _frag_body.__fragment__(fragment_font_variant_fragment())
    return _frag


def fragment_font_variant_fragment():
    _frag = sgqlc.operation.Fragment(_schema.FontVariant, 'FontVariantFragment')
    _frag.font_size()
    _frag.font_weight()
    return _frag


def fragment_layout_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallLayoutConfiguration, 'LayoutConfigurationFragment')
    _frag.alignment()
    _frag.plan_width()
    _frag.plan_margin()
    _frag.plan_padding()
    return _frag


def fragment_paywall_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallConfiguration, 'PaywallConfigurationFragment')
    _frag_palette = _frag.palette()
    _frag_palette.primary()
    _frag_palette.text_color()
    _frag_palette.background_color()
    _frag_palette.border_color()
    _frag_palette.current_plan_background()
    _frag_typography = _frag.typography()
    _frag_typography.__fragment__(fragment_typography_configuration_fragment())
    _frag_layout = _frag.layout()
    _frag_layout.__fragment__(fragment_layout_configuration_fragment())
    _frag.custom_css()
    return _frag


def fragment_paywall_currency():
    _frag = sgqlc.operation.Fragment(_schema.PaywallCurrency, 'PaywallCurrency')
    _frag.code()
    _frag.symbol()
    return _frag


def fragment_product_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Product, 'ProductFragment')
    _frag.ref_id()
    _frag.display_name()
    _frag.description()
    _frag.additional_meta_data()
    _frag_product_settings = _frag.product_settings()
    _frag_product_settings_downgrade_plan = _frag_product_settings.downgrade_plan()
    _frag_product_settings_downgrade_plan.ref_id()
    _frag_product_settings_downgrade_plan.display_name()
    return _frag


def fragment_entitlements_updated_payload():
    _frag = sgqlc.operation.Fragment(_schema.EntitlementsUpdated, 'EntitlementsUpdatedPayload')
    _frag.customer_id()
    _frag.resource_id()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_entitlement_fragment())
    return _frag


def fragment_entitlement_usage_updated():
    _frag = sgqlc.operation.Fragment(_schema.UsageUpdated, 'EntitlementUsageUpdated')
    _frag_usage = _frag.usage()
    _frag_usage.__fragment__(fragment_usage_updated_fragment())
    _frag_entitlement = _frag.entitlement()
    _frag_entitlement.__fragment__(fragment_entitlement_fragment())
    return _frag


def fragment_customer_portal_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortal, 'CustomerPortalFragment')
    _frag_subscriptions = _frag.subscriptions()
    _frag_subscriptions.__fragment__(fragment_customer_portal_subscription_fragment())
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_customer_portal_entitlement())
    _frag_promotional_entitlements = _frag.promotional_entitlements()
    _frag_promotional_entitlements.__fragment__(fragment_customer_portal_promotional_entitlement())
    _frag_billing_information = _frag.billing_information()
    _frag_billing_information.__fragment__(fragment_customer_portal_billing_information())
    _frag.show_watermark()
    _frag.billing_portal_url()
    _frag.can_upgrade_subscription()
    _frag_configuration = _frag.configuration()
    _frag_configuration.__fragment__(fragment_customer_portal_configuration_fragment())
    _frag_resource = _frag.resource()
    _frag_resource.__fragment__(fragment_customer_resource_fragment())
    return _frag


def fragment_customer_portal_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalConfiguration, 'CustomerPortalConfigurationFragment')
    _frag_palette = _frag.palette()
    _frag_palette.primary()
    _frag_palette.text_color()
    _frag_palette.background_color()
    _frag_palette.border_color()
    _frag_palette.current_plan_background()
    _frag_palette.icons_color()
    _frag_palette.paywall_background_color()
    _frag_typography = _frag.typography()
    _frag_typography.__fragment__(fragment_typography_configuration_fragment())
    _frag.custom_css()
    return _frag


def fragment_customer_portal_subscription_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalSubscription, 'CustomerPortalSubscriptionFragment')
    _frag.subscription_id()
    _frag.plan_name()
    _frag_pricing = _frag.pricing()
    _frag_pricing.unit_quantity()
    _frag_pricing.billing_period()
    _frag_pricing.billing_model()
    _frag_pricing.pricing_type()
    _frag_pricing.usage_based_estimated_bill()
    _frag_pricing_price = _frag_pricing.price()
    _frag_pricing_price.amount()
    _frag_pricing_price.currency()
    _frag_pricing_feature = _frag_pricing.feature()
    _frag_pricing_feature.feature_units()
    _frag_pricing_feature.feature_units_plural()
    _frag_pricing_feature.display_name()
    _frag.status()
    _frag.trial_remaining_days()
    _frag_billing_period_range = _frag.billing_period_range()
    _frag_billing_period_range.start()
    _frag_billing_period_range.end()
    _frag_total_price = _frag.total_price()
    _frag_total_price_sub_total = _frag_total_price.sub_total()
    _frag_total_price_sub_total.amount()
    _frag_total_price_total = _frag_total_price.total()
    _frag_total_price_total.amount()
    _frag_total_price_addons_total = _frag_total_price.addons_total()
    _frag_total_price_addons_total.amount()
    _frag_addons = _frag.addons()
    _frag_addons.__fragment__(fragment_customer_portal_subscription_addon())
    _frag_scheduled_updates = _frag.scheduled_updates()
    _frag_scheduled_updates.__fragment__(fragment_customer_portal_subscription_scheduled_update_data())
    return _frag


def fragment_customer_portal_subscription_addon():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalAddon, 'CustomerPortalSubscriptionAddon')
    _frag.addon_id()
    _frag.description()
    _frag.display_name()
    _frag.quantity()
    return _frag


def fragment_customer_portal_subscription_scheduled_update_data():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionScheduledUpdate, 'CustomerPortalSubscriptionScheduledUpdateData')
    _frag.subscription_schedule_type()
    _frag.schedule_status()
    _frag.scheduled_execution_time()
    _frag_target_package = _frag.target_package()
    _frag_target_package.id()
    _frag_target_package.ref_id()
    _frag_target_package.display_name()
    _frag_schedule_variables = _frag.schedule_variables()
    _frag_schedule_variables__as__DowngradeChangeVariables = _frag_schedule_variables.__as__(_schema.DowngradeChangeVariables)
    _frag_schedule_variables__as__DowngradeChangeVariables.addon_ref_ids()
    _frag_schedule_variables__as__DowngradeChangeVariables.billing_period()
    _frag_schedule_variables__as__DowngradeChangeVariables.downgrade_plan_ref_id()
    _frag_schedule_variables__as__BillingPeriodChangeVariables = _frag_schedule_variables.__as__(_schema.BillingPeriodChangeVariables)
    _frag_schedule_variables__as__BillingPeriodChangeVariables.billing_period()
    _frag_schedule_variables__as__UnitAmountChangeVariables = _frag_schedule_variables.__as__(_schema.UnitAmountChangeVariables)
    _frag_schedule_variables__as__UnitAmountChangeVariables.new_unit_amount()
    return _frag


def fragment_customer_portal_entitlement():
    _frag = sgqlc.operation.Fragment(_schema.Entitlement, 'CustomerPortalEntitlement')
    _frag.is_granted()
    _frag.usage_limit()
    _frag.current_usage()
    _frag.has_unlimited_usage()
    _frag.next_reset_date()
    _frag.reset_period()
    _frag_reset_period_configuration = _frag.reset_period_configuration()
    _frag_reset_period_configuration.__fragment__(fragment_reset_period_configuration_fragment())
    _frag_feature = _frag.feature()
    _frag_feature.__fragment__(fragment_feature_fragment())
    return _frag


def fragment_customer_portal_promotional_entitlement():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalPromotionalEntitlement, 'CustomerPortalPromotionalEntitlement')
    _frag.display_name()
    _frag.has_unlimited_usage()
    _frag.usage_limit()
    _frag.period()
    _frag.start_date()
    _frag.end_date()
    return _frag


def fragment_customer_portal_billing_information():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalBillingInformation, 'CustomerPortalBillingInformation')
    _frag.email()
    _frag.name()
    _frag.default_payment_method_last4_digits()
    _frag.default_payment_method_id()
    _frag.default_payment_method_last4_digits()
    _frag.default_payment_expiration_month()
    _frag.default_payment_expiration_year()
    return _frag


def fragment_mock_paywall_plan_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallPlan, 'MockPaywallPlanFragment')
    _frag.ref_id()
    _frag.description()
    _frag.display_name()
    _frag.billing_id()
    _frag.additional_meta_data()
    _frag_product = _frag.product()
    _frag_product.ref_id()
    _frag_product.display_name()
    _frag_product.description()
    _frag_product.additional_meta_data()
    _frag_base_plan = _frag.base_plan()
    _frag_base_plan.ref_id()
    _frag_base_plan.display_name()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_mock_paywall_package_entitlement_fragment())
    _frag_inherited_entitlements = _frag.inherited_entitlements()
    _frag_inherited_entitlements.__fragment__(fragment_mock_paywall_package_entitlement_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_mock_paywall_price_fragment())
    _frag.pricing_type()
    _frag_default_trial_config = _frag.default_trial_config()
    _frag_default_trial_config.duration()
    _frag_default_trial_config.units()
    _frag_compatible_addons = _frag.compatible_addons()
    _frag_compatible_addons.__fragment__(fragment_mock_paywall_addon_fragment())
    return _frag


def fragment_mock_paywall_package_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Entitlement, 'MockPaywallPackageEntitlementFragment')
    _frag.usage_limit()
    _frag.has_unlimited_usage()
    _frag.reset_period()
    _frag.hidden_from_widgets()
    _frag.display_name_override()
    _frag_feature = _frag.feature()
    _frag_feature.feature_type()
    _frag_feature.meter_type()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    _frag_feature.ref_id()
    _frag_feature.additional_meta_data()
    return _frag


def fragment_mock_paywall_price_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallPrice, 'MockPaywallPriceFragment')
    _frag.billing_model()
    _frag.billing_period()
    _frag.billing_id()
    _frag.min_unit_quantity()
    _frag.max_unit_quantity()
    _frag.billing_country_code()
    _frag_price = _frag.price()
    _frag_price.amount()
    _frag_price.currency()
    _frag_feature = _frag.feature()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    return _frag


def fragment_mock_paywall_addon_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallAddon, 'MockPaywallAddonFragment')
    _frag.ref_id()
    _frag.display_name()
    _frag.description()
    _frag.additional_meta_data()
    _frag.billing_id()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_mock_paywall_package_entitlement_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_mock_paywall_price_fragment())
    _frag.pricing_type()
    return _frag


def fragment_paywall_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Paywall, 'PaywallFragment')
    _frag_plans = _frag.plans()
    _frag_plans.__fragment__(fragment_plan_fragment())
    _frag_currency = _frag.currency()
    _frag_currency.__fragment__(fragment_paywall_currency())
    _frag_configuration = _frag.configuration()
    _frag_configuration.__fragment__(fragment_paywall_configuration_fragment())
    _frag_customer = _frag.customer()
    _frag_customer.__fragment__(fragment_customer_fragment())
    _frag_active_subscriptions = _frag.active_subscriptions()
    _frag_active_subscriptions.__fragment__(fragment_subscription_fragment())
    _frag_resource = _frag.resource()
    _frag_resource.__fragment__(fragment_customer_resource_fragment())
    return _frag


class Fragment:
    addon_fragment = fragment_addon_fragment()
    coupon_fragment = fragment_coupon_fragment()
    customer_fragment = fragment_customer_fragment()
    customer_portal_billing_information = fragment_customer_portal_billing_information()
    customer_portal_configuration_fragment = fragment_customer_portal_configuration_fragment()
    customer_portal_entitlement = fragment_customer_portal_entitlement()
    customer_portal_fragment = fragment_customer_portal_fragment()
    customer_portal_promotional_entitlement = fragment_customer_portal_promotional_entitlement()
    customer_portal_subscription_addon = fragment_customer_portal_subscription_addon()
    customer_portal_subscription_fragment = fragment_customer_portal_subscription_fragment()
    customer_portal_subscription_scheduled_update_data = fragment_customer_portal_subscription_scheduled_update_data()
    customer_resource_fragment = fragment_customer_resource_fragment()
    customer_with_subscriptions_fragment = fragment_customer_with_subscriptions_fragment()
    entitlement_fragment = fragment_entitlement_fragment()
    entitlement_usage_updated = fragment_entitlement_usage_updated()
    entitlements_updated_payload = fragment_entitlements_updated_payload()
    feature_fragment = fragment_feature_fragment()
    font_variant_fragment = fragment_font_variant_fragment()
    layout_configuration_fragment = fragment_layout_configuration_fragment()
    mock_paywall_addon_fragment = fragment_mock_paywall_addon_fragment()
    mock_paywall_package_entitlement_fragment = fragment_mock_paywall_package_entitlement_fragment()
    mock_paywall_plan_fragment = fragment_mock_paywall_plan_fragment()
    mock_paywall_price_fragment = fragment_mock_paywall_price_fragment()
    package_entitlement_fragment = fragment_package_entitlement_fragment()
    paywall_addon_fragment = fragment_paywall_addon_fragment()
    paywall_configuration_fragment = fragment_paywall_configuration_fragment()
    paywall_currency = fragment_paywall_currency()
    paywall_fragment = fragment_paywall_fragment()
    paywall_package_entitlement_fragment = fragment_paywall_package_entitlement_fragment()
    paywall_plan_fragment = fragment_paywall_plan_fragment()
    plan_fragment = fragment_plan_fragment()
    price_fragment = fragment_price_fragment()
    product_fragment = fragment_product_fragment()
    promotional_entitlement_fragment = fragment_promotional_entitlement_fragment()
    reset_period_configuration_fragment = fragment_reset_period_configuration_fragment()
    slim_customer_fragment = fragment_slim_customer_fragment()
    slim_subscription_fragment = fragment_slim_subscription_fragment()
    subscription_fragment = fragment_subscription_fragment()
    subscription_preview_fragment = fragment_subscription_preview_fragment()
    subscription_scheduled_update_data = fragment_subscription_scheduled_update_data()
    total_price_fragment = fragment_total_price_fragment()
    typography_configuration_fragment = fragment_typography_configuration_fragment()
    usage_updated_fragment = fragment_usage_updated_fragment()


def mutation_provision_customer():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ProvisionCustomer', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ProvisionCustomerInput))))
    _op_provision_customer = _op.provision_customer(input=sgqlc.types.Variable('input'))
    _op_provision_customer_customer = _op_provision_customer.customer()
    _op_provision_customer_customer.__fragment__(fragment_slim_customer_fragment())
    _op_provision_customer.subscription_decision_strategy()
    _op_provision_customer_subscription = _op_provision_customer.subscription()
    _op_provision_customer_subscription.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_import_customer_bulk():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ImportCustomerBulk', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ImportCustomerBulk))))
    _op.import_customers_bulk(input=sgqlc.types.Variable('input'))
    return _op


def mutation_import_customer():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ImportCustomer', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ImportCustomerInput))))
    _op_import_customer = _op.import_one_customer(input=sgqlc.types.Variable('input'), __alias__='import_customer')
    _op_import_customer.__fragment__(fragment_slim_customer_fragment())
    return _op


def mutation_update_customer():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='UpdateCustomer', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.UpdateCustomerInput))))
    _op_update_customer = _op.update_one_customer(input=sgqlc.types.Variable('input'), __alias__='update_customer')
    _op_update_customer.__fragment__(fragment_slim_customer_fragment())
    return _op


def mutation_provision_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ProvisionSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ProvisionSubscriptionInput))))
    _op_provision_subscription = _op.provision_subscription_v2(input=sgqlc.types.Variable('input'), __alias__='provision_subscription')
    _op_provision_subscription.checkout_url()
    _op_provision_subscription.status()
    _op_provision_subscription_subscription = _op_provision_subscription.subscription()
    _op_provision_subscription_subscription.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_import_subscriptions_bulk():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ImportSubscriptionsBulk', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ImportSubscriptionsBulk))))
    _op.import_subscriptions_bulk(input=sgqlc.types.Variable('input'))
    return _op


def mutation_update_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='UpdateSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.UpdateSubscriptionInput))))
    _op_update_subscription = _op.update_one_subscription(input=sgqlc.types.Variable('input'), __alias__='update_subscription')
    _op_update_subscription.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_cancel_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='CancelSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.SubscriptionCancellationInput))))
    _op_cancel_subscription = _op.cancel_subscription(input=sgqlc.types.Variable('input'))
    _op_cancel_subscription.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_initiate_checkout():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='InitiateCheckout', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.InitiateCheckoutInput))))
    _op_initiate_checkout = _op.initiate_checkout(input=sgqlc.types.Variable('input'))
    _op_initiate_checkout.checkout_url()
    _op_initiate_checkout.checkout_billing_id()
    return _op


def mutation_estimate_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='EstimateSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.EstimateSubscriptionInput))))
    _op_estimate_subscription = _op.estimate_subscription(input=sgqlc.types.Variable('input'))
    _op_estimate_subscription.__fragment__(fragment_subscription_preview_fragment())
    return _op


def mutation_estimate_subscription_update():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='EstimateSubscriptionUpdate', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.EstimateSubscriptionUpdateInput))))
    _op_estimate_subscription_update = _op.estimate_subscription_update(input=sgqlc.types.Variable('input'))
    _op_estimate_subscription_update.__fragment__(fragment_subscription_preview_fragment())
    return _op


def mutation_cancel_subscription_updates():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='CancelSubscriptionUpdates', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.SubscriptionUpdateScheduleCancellationInput))))
    _op.cancel_schedule(input=sgqlc.types.Variable('input'))
    return _op


def mutation_report_usage():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ReportUsage', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.UsageMeasurementCreateInput))))
    _op_create_usage_measurement = _op.create_usage_measurement(usage_measurement=sgqlc.types.Variable('input'))
    _op_create_usage_measurement.id()
    _op_create_usage_measurement.current_usage()
    _op_create_usage_measurement.next_reset_date()
    _op_create_usage_measurement.timestamp()
    return _op


def mutation_report_entitlement_check_requested():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ReportEntitlementCheckRequested', variables=dict(entitlementCheckRequested=sgqlc.types.Arg(sgqlc.types.non_null(_schema.EntitlementCheckRequested))))
    _op.report_entitlement_check_requested(entitlement_check_requested=sgqlc.types.Variable('entitlementCheckRequested'))
    return _op


def mutation_create_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='CreateSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.SubscriptionInput))))
    _op_create_subscription = _op.create_subscription(subscription=sgqlc.types.Variable('input'))
    _op_create_subscription.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_migrate_subscription_to_latest():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='MigrateSubscriptionToLatest', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.SubscriptionMigrationInput))))
    _op_migrate_subscription_to_latest = _op.migrate_subscription_to_latest(input=sgqlc.types.Variable('input'))
    _op_migrate_subscription_to_latest.subscription_id()
    return _op


class Mutation:
    cancel_subscription = mutation_cancel_subscription()
    cancel_subscription_updates = mutation_cancel_subscription_updates()
    create_subscription = mutation_create_subscription()
    estimate_subscription = mutation_estimate_subscription()
    estimate_subscription_update = mutation_estimate_subscription_update()
    import_customer = mutation_import_customer()
    import_customer_bulk = mutation_import_customer_bulk()
    import_subscriptions_bulk = mutation_import_subscriptions_bulk()
    initiate_checkout = mutation_initiate_checkout()
    migrate_subscription_to_latest = mutation_migrate_subscription_to_latest()
    provision_customer = mutation_provision_customer()
    provision_subscription = mutation_provision_subscription()
    report_entitlement_check_requested = mutation_report_entitlement_check_requested()
    report_usage = mutation_report_usage()
    update_customer = mutation_update_customer()
    update_subscription = mutation_update_subscription()


def query_get_customer_by_id():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCustomerById', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetCustomerByRefIdInput))))
    _op_get_customer_by_ref_id = _op.get_customer_by_ref_id(input=sgqlc.types.Variable('input'))
    _op_get_customer_by_ref_id.__fragment__(fragment_customer_with_subscriptions_fragment())
    return _op


def query_get_active_subscriptions():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetActiveSubscriptions', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetActiveSubscriptionsInput))))
    _op_get_active_subscriptions = _op.get_active_subscriptions(input=sgqlc.types.Variable('input'))
    _op_get_active_subscriptions.__fragment__(fragment_subscription_fragment())
    return _op


def query_get_coupons():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCoupons')
    _op_coupons = _op.coupons(filter={'status': {'eq': 'ACTIVE'}}, paging={'first': 50})
    _op_coupons_edges = _op_coupons.edges()
    _op_coupons_edges_node = _op_coupons_edges.node()
    _op_coupons_edges_node.__fragment__(fragment_coupon_fragment())
    return _op


def query_get_paywall():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetPaywall', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetPaywallInput))))
    _op_paywall = _op.paywall(input=sgqlc.types.Variable('input'))
    _op_paywall.__fragment__(fragment_paywall_fragment())
    return _op


def query_get_entitlements():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetEntitlements', variables=dict(query=sgqlc.types.Arg(sgqlc.types.non_null(_schema.FetchEntitlementsQuery))))
    _op_entitlements = _op.cached_entitlements(query=sgqlc.types.Variable('query'), __alias__='entitlements')
    _op_entitlements.__fragment__(fragment_entitlement_fragment())
    return _op


def query_get_entitlement():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetEntitlement', variables=dict(query=sgqlc.types.Arg(sgqlc.types.non_null(_schema.FetchEntitlementQuery))))
    _op_entitlement = _op.entitlement(query=sgqlc.types.Variable('query'))
    _op_entitlement.__fragment__(fragment_entitlement_fragment())
    return _op


def query_get_products():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetProducts')
    _op_products = _op.products(paging={'first': 50})
    _op_products_edges = _op_products.edges()
    _op_products_edges_node = _op_products_edges.node()
    _op_products_edges_node.__fragment__(fragment_product_fragment())
    return _op


def query_get_sdk_configuration():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetSdkConfiguration')
    _op_sdk_configuration = _op.sdk_configuration()
    _op_sdk_configuration.sentry_dsn()
    _op_sdk_configuration.is_widget_watermark_enabled()
    return _op


def query_get_customer_portal_by_ref_id():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCustomerPortalByRefId', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.CustomerPortalInput))))
    _op_customer_portal = _op.customer_portal(input=sgqlc.types.Variable('input'))
    _op_customer_portal.__fragment__(fragment_customer_portal_fragment())
    return _op


def query_get_mock_paywall():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetMockPaywall', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetPaywallInput))))
    _op_mock_paywall = _op.mock_paywall(input=sgqlc.types.Variable('input'))
    _op_mock_paywall_plans = _op_mock_paywall.plans()
    _op_mock_paywall_plans.__fragment__(fragment_mock_paywall_plan_fragment())
    _op_mock_paywall_configuration = _op_mock_paywall.configuration()
    _op_mock_paywall_configuration.__fragment__(fragment_paywall_configuration_fragment())
    return _op


class Query:
    get_active_subscriptions = query_get_active_subscriptions()
    get_coupons = query_get_coupons()
    get_customer_by_id = query_get_customer_by_id()
    get_customer_portal_by_ref_id = query_get_customer_portal_by_ref_id()
    get_entitlement = query_get_entitlement()
    get_entitlements = query_get_entitlements()
    get_mock_paywall = query_get_mock_paywall()
    get_paywall = query_get_paywall()
    get_products = query_get_products()
    get_sdk_configuration = query_get_sdk_configuration()


def subscription_entitlements_updated():
    _op = sgqlc.operation.Operation(_schema_root.subscription_type, name='EntitlementsUpdated')
    _op_entitlements_updated = _op.entitlements_updated()
    _op_entitlements_updated.__fragment__(fragment_entitlements_updated_payload())
    return _op


def subscription_usage_updated():
    _op = sgqlc.operation.Operation(_schema_root.subscription_type, name='UsageUpdated')
    _op_usage_updated = _op.usage_updated()
    _op_usage_updated.__fragment__(fragment_entitlement_usage_updated())
    return _op


class Subscription:
    entitlements_updated = subscription_entitlements_updated()
    usage_updated = subscription_usage_updated()


class Operations:
    fragment = Fragment
    mutation = Mutation
    query = Query
    subscription = Subscription
