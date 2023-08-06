<template>
  <main-container>
    <div v-if="orderForm && orderSent">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2" color="success">mdi-check-circle-outline</v-icon>
          {{ $t("order.submitted.thank_you") }}
        </v-card-title>
        <v-card-text class="text-body-1 black--text">
          {{ $t("order.submitted.submitted_successfully") }}
          <strong>{{ $t("order.submitted.confirm_necessary") }}</strong>
        </v-card-text>
      </v-card>
    </div>
    <div v-else-if="orderForm">
      <h1 class="text-h4 mb-4">{{ orderForm.title }}</h1>
      <v-stepper v-model="step" class="mb-4">
        <v-stepper-header>
          <v-stepper-step :complete="step > 1" step="1">
            {{ $t("order.steps.items") }}
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step :complete="step > 2" step="2">
            {{ $t("order.steps.shipping") }}
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step :complete="step > 3" step="3">
            {{ $t("order.steps.payment") }}
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step :complete="step > 4" step="4">
            {{ $t("order.steps.confirm") }}
          </v-stepper-step>
          <v-divider></v-divider>
        </v-stepper-header>
        <v-stepper-items>
          <v-stepper-content step="1">
            <h2 class="text-h6 mb-4">{{ $t("order.personal_data.title") }}</h2>
            <message-box v-if="personalDataImported" type="info" class="mb-4">
              {{ $t("order.personal_data.imported") }}
            </message-box>
            <div class="mb-4">
              <v-text-field
                outlined
                v-model="data.fullName"
                :label="$t('order.personal_data.label_name')"
                required
                :counter="255"
                :rules="rules.name"
                prepend-icon="mdi-account-outline"
              ></v-text-field>
              <v-text-field
                outlined
                v-model="data.email"
                :label="$t('order.personal_data.label_email')"
                required
                :counter="255"
                :rules="rules.email"
                prepend-icon="mdi-email-outline"
              ></v-text-field>
            </div>
            <h2 class="text-h6 mb-4">{{ $t("order.items.title") }}</h2>
            <order-item
              v-for="(item, index) in itemsWithData"
              :key="item.id"
              :item="item"
              @update-count="updateCount"
            />
            <v-divider class="mb-4" />
            <total-row :total="total" :total-count="totalCount" class="mb-4" />
            <control-row
              :step="step"
              :next-disabled="totalCount < 1"
              @set-step="setStep"
            />
          </v-stepper-content>

          <v-stepper-content step="2">
            <h2 class="text-h6 mb-4">{{ $t("order.shipping.title") }}</h2>

            <v-radio-group
              v-model="data.shippingOption"
              :rules="rules.shippingOption"
              mandatory
            >
              <option-radio
                v-for="(option, index) in shippingOptionsWithData"
                :key="option.id"
                :option="option"
                :disabled="
                  option.forDigitalProducts
                    ? !downloadEnabled
                    : !normalShippingEnabled
                "
              />
            </v-radio-group>
            <div
              v-if="
                selectedShippingOption &&
                selectedShippingOption.addressNecessary
              "
            >
              <h2 class="text-h6 mb-4">{{ $t("order.shipping.address") }}</h2>
              <v-form v-model="shippingAddressFormValid">
                <v-text-field
                  outlined
                  v-model="data.shippingFullName"
                  :label="$t('order.shipping.label_name')"
                  required
                  :counter="255"
                  :rules="rules.name"
                  prepend-icon="mdi-account-outline"
                />
                <v-text-field
                  outlined
                  v-model="data.secondAddressRow"
                  :label="$t('order.shipping.label_second_address_row')"
                  :counter="255"
                  prepend-icon="mdi-account-arrow-right-outline"
                />
                <v-row>
                  <v-col cols="12" sm="12" md="8" lg="10">
                    <v-text-field
                      outlined
                      v-model="data.street"
                      :label="$t('order.shipping.label_street')"
                      required
                      :counter="255"
                      :rules="rules.street"
                      prepend-icon="mdi-home-outline"
                    />
                  </v-col>
                  <v-col cols="12" sm="12" md="4" lg="2">
                    <v-text-field
                      outlined
                      v-model="data.housenumber"
                      :label="$t('order.shipping.label_housenumber')"
                      required
                      :counter="255"
                      :rules="rules.housenumber"
                    />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" sm="12" md="4" lg="2">
                    <v-text-field
                      outlined
                      v-model="data.plz"
                      :label="$t('order.shipping.label_postal_code')"
                      required
                      :rules="rules.postalCode"
                      prepend-icon="mdi-home-city-outline"
                    />
                  </v-col>
                  <v-col cols="12" sm="12" md="8" lg="10">
                    <v-text-field
                      outlined
                      v-model="data.place"
                      :label="$t('order.shipping.label_place')"
                      required
                      :counter="255"
                      :rules="rules.place"
                    />
                  </v-col>
                </v-row>
              </v-form>
            </div>
            <control-row
              :step="step"
              :next-disabled="!shippingOptionValid"
              @set-step="setStep"
            />
          </v-stepper-content>
          <v-stepper-content step="3">
            <h2 class="text-h6 mb-4">{{ $t("order.payment.title") }}</h2>

            <v-radio-group
              v-model="data.paymentOption"
              :rules="rules.paymentOption"
              mandatory
            >
              <option-radio
                v-for="(option, index) in paymentOptionsWithData"
                :key="option.id"
                :option="option"
              />
            </v-radio-group>
            <control-row
              :step="step"
              :next-disabled="!selectedPaymentOption"
              @set-step="setStep"
            />
          </v-stepper-content>
          <v-stepper-content step="4">
            <h2 class="text-h6 mb-4">{{ $t("order.personal_data.title") }}</h2>
            <v-list class="mb-4">
              <v-list-item>
                <v-list-item-content>
                  <v-row>
                    <v-col class="text-body-1 font-weight-medium">
                      <v-icon color="primary" left class="mr-4"
                        >mdi-account-outline</v-icon
                      >
                      {{ $t("order.personal_data.label_name") }}
                    </v-col>
                    <v-col class="text-body-1">
                      {{ data.fullName }}
                    </v-col>
                  </v-row>
                </v-list-item-content>
              </v-list-item>
              <v-divider />
              <v-list-item>
                <v-list-item-content>
                  <v-row>
                    <v-col class="text-body-1 font-weight-medium">
                      <v-icon color="primary" left class="mr-4"
                        >mdi-email-outline</v-icon
                      >
                      {{ $t("order.personal_data.label_email") }}
                    </v-col>
                    <v-col class="text-body-1">
                      {{ data.email }}
                    </v-col>
                  </v-row>
                </v-list-item-content>
              </v-list-item>
              <v-divider
                v-if="
                  selectedShippingOption &&
                  selectedShippingOption.addressNecessary
                "
              />
              <v-list-item
                v-if="
                  selectedShippingOption &&
                  selectedShippingOption.addressNecessary
                "
              >
                <v-list-item-content>
                  <v-row>
                    <v-col class="text-body-1 font-weight-medium">
                      <v-icon color="primary" left class="mr-4"
                        >mdi-home-city-outline</v-icon
                      >
                      {{ $t("order.shipping.address") }}
                    </v-col>
                    <v-col class="text-body-1">
                      {{ data.shippingFullName }} <br />
                      {{ data.secondAddressRow }} <br />
                      {{ data.street }} {{ data.housenumber }}<br />
                      {{ data.plz }} {{ data.place }}
                    </v-col>
                  </v-row>
                </v-list-item-content>
              </v-list-item>
            </v-list>

            <h2 class="text-h6 mb-4">{{ $t("order.items.title") }}</h2>
            <div class="mb-4">
              <order-item
                v-for="(item, index) in itemsWithCount"
                :key="item.id"
                :item="item"
                read-only
              />
            </div>

            <v-divider class="mb-4" />
            <option-row
              :option="selectedShippingOption"
              v-if="selectedShippingOption"
            />
            <option-row
              :option="selectedPaymentOption"
              v-if="selectedPaymentOption"
            />
            <v-divider class="my-4" />
            <total-row :total="total" :total-count="totalCount" class="mb-4" />

            <h2 class="text-h6 mb-4">{{ $t("order.confirm.title_notes") }}</h2>
            <v-textarea
              outlined
              v-model="data.notes"
              :label="$t('order.confirm.label_notes')"
              prepend-icon="mdi-information-outline"
              class="mb-4"
            />

            <message-box type="info" class="mb-4">
              {{ $t("order.confirm.hint") }}
            </message-box>
            <ApolloMutation
              :mutation="require('./orderMutation.graphql')"
              :variables="{
                orderForm: orderForm.id,
                accessCode: accessCode,
                order: dataForSubmit,
              }"
              @done="orderDone"
            >
              <template #default="{ mutate, loading, error }">
                <control-row
                  :step="step"
                  final-step
                  @set-step="setStep"
                  @confirm="mutate"
                  :next-loading="loading"
                />
              </template>
            </ApolloMutation>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
      <v-card>
        <v-card-text>
          <div v-html="orderForm.helpText" />
        </v-card-text>
      </v-card>
    </div>
    <div v-else>
      <v-card :loading="$apollo.queries.orderForm.loading">
        <v-card-title>
          {{ $t("order.access.title") }}
        </v-card-title>
        <v-card-text>
          <div class="body-2 mb-3">
            {{ $t("order.access.hint") }}
          </div>
          <v-text-field
            v-model="accessCode"
            :label="$t('order.access.label')"
            type="password"
            outlined
            prepend-inner-icon="mdi-form-textbox-password"
            autofocus
          ></v-text-field>
        </v-card-text>
      </v-card>
    </div>
  </main-container>
</template>

<script>
import OrderItem from "./OrderItem.vue";
import TotalRow from "./TotalRow.vue";
import ControlRow from "./ControlRow.vue";
import OptionRow from "./OptionRow.vue";
import OptionRadio from "./OptionRadio.vue";
import MainContainer from "./MainContainer.vue";
import gqlWhoAmI from "./whoAmI.graphql";
import gqlOrderForm from "./OrderForm.graphql";

export default {
  name: "OrderForm",
  components: {
    MainContainer,
    OptionRadio,
    OptionRow,
    ControlRow,
    TotalRow,
    OrderItem,
  },
  apollo: {
    orderForm() {
      return {
        query: gqlOrderForm,
        variables() {
          return {
            id: this.$route.params.formId,
            accessCode: this.accessCode,
          };
        },
        notifyOnNetworkStatusChange: true,
      };
    },
    whoAmI: {
      query: gqlWhoAmI,
    },
  },
  watch: {
    whoAmI(val) {
      if (val && val.person) {
        if (!this.fullName || !this.email) {
          this.personalDataImported = true;
          this.data.fullName = val.person.fullName;
          this.data.email = val.person.email;
        }
      }
    },
    itemsWithData(val) {
      if (val) {
        for (const item of val) {
          if (item.id in this.orderedItems) {
            return;
          }
          this.$set(this.orderedItems, item.id, {
            count: 0,
          });
        }
      }
    },
    downloadEnabled(val) {
      if (!this.selectedShippingOption) {
        return;
      }
      if (
        (this.selectedShippingOption.forDigitalProducts && !val) ||
        (!this.selectedShippingOption.forDigitalProducts && val)
      ) {
        this.data.shippingOption = null;
      }
    },
    normalShippingEnabled(val) {
      if (!this.selectedShippingOption) {
        return;
      }
      if (
        (this.selectedShippingOption.forDigitalProducts && val) ||
        (!this.selectedShippingOption.forDigitalProducts && !val)
      ) {
        this.data.shippingOption = null;
      }
    },
  },
  methods: {
    updateCount(item, count) {
      this.$set(this.orderedItems[item.id], "count", count);
    },
    setStep(step) {
      this.step = step;
    },
    orderDone({ data }) {
      if (data.sendOrder.ok) {
        this.orderSent = true;
      }
      console.log(data);
      console.log("ORDER DONE");
    },
  },
  computed: {
    rules() {
      return {
        name: [
          (v) => !!v || this.$t("order.rules.name.required"),
          (v) => v.length <= 255 || this.$t("order.rules.name.max"),
        ],
        email: [
          (v) => !!v || this.$t("order.rules.email.required"),
          (v) => /.+@.+\..+/.test(v) || this.$t("order.rules.email.valid"),
        ],
        shippingOption: [
          (v) => !!v || this.$t("order.rules.shipping_option.required"),
        ],
        paymentOption: [
          (v) => !!v || this.$t("order.rules.payment_option.required"),
        ],
        street: [
          (v) => !!v || this.$t("order.rules.street.required"),
          (v) => v.length <= 255 || this.$t("order.rules.street.max"),
        ],
        housenumber: [
          (v) => !!v || this.$t("order.rules.housenumber.required"),
          (v) => v.length <= 255 || this.$t("order.rules.housenumber.max"),
        ],
        postalCode: [
          (v) => !!v || this.$t("order.rules.postal_code.required"),
          (v) => /^\d{5}$/.test(v) || this.$t("order.rules.postal_code.valid"),
        ],
        place: [
          (v) => !!v || this.$t("order.rules.place.required"),
          (v) => v.length <= 255 || this.$t("order.rules.place.max"),
        ],
      };
    },
    itemsWithData() {
      if (!this.orderForm) {
        return [];
      }
      return [...this.orderForm.availableItems]
        .sort((a, b) => a.order < b.order)
        .map((item) => {
          const data =
            item.id in this.orderedItems ? this.orderedItems[item.id] : {};
          return {
            ...item,
            count: data.count ? data.count : 0,
            total: data.count ? data.count * item.price : 0,
          };
        });
    },
    itemsWithCount() {
      return this.itemsWithData.filter((item) => item.count > 0);
    },
    shippingOptionsWithData() {
      if (!this.orderForm) {
        return [];
      }
      const totalCount = this.totalCountShipping;
      return this.orderForm.availableShippingOptions.map(function (option) {
        const prices = option.prices.filter(function (price) {
          return totalCount >= price.minCount && totalCount <= price.maxCount;
        });
        let price = 0;
        if (prices.length > 0) {
          price = prices[0].price;
        }
        return {
          ...option,
          price: price,
        };
      });
    },
    paymentOptionsWithData() {
      if (!this.orderForm) {
        return [];
      }
      return this.orderForm.availablePaymentOptions;
    },
    total() {
      return this.itemsWithData.reduce((acc, item) => acc + item.total, 0);
    },
    totalCount() {
      return this.itemsWithData.reduce((acc, item) => acc + item.count, 0);
    },
    totalCountShipping() {
      return this.itemsWithData
        .filter((item) => item.countForShipping)
        .reduce((acc, item) => acc + item.count, 0);
    },
    selectedShippingOption() {
      if (!this.data.shippingOption) {
        return null;
      }
      return this.shippingOptionsWithData.find(
        (option) => option.id === this.data.shippingOption
      );
    },
    shippingOptionValid() {
      if (!this.selectedShippingOption) {
        return false;
      }
      if (this.selectedShippingOption.addressNecessary) {
        return this.shippingAddressFormValid;
      }
      return true;
    },
    selectedPaymentOption() {
      if (!this.data.paymentOption) {
        return null;
      }
      return this.paymentOptionsWithData.find(
        (option) => option.id === this.data.paymentOption
      );
    },
    downloadEnabled() {
      return (
        this.totalCount > 0 &&
        this.itemsWithCount.every((item) => item.digitalProduct)
      );
    },
    normalShippingEnabled() {
      return (
        this.totalCount > 0 &&
        this.itemsWithCount.some((item) => !item.digitalProduct)
      );
    },
    dataForSubmit() {
      return {
        ...this.data,
        items: this.itemsWithCount.map((item) => {
          return {
            item: item.id,
            count: item.count,
          };
        }),
      };
    },
  },
  data() {
    return {
      orderSent: false,
      accessCode: "",
      step: 1,
      personalDataImported: false,
      data: {
        fullName: "",
        email: "",
        notes: "",
        shippingOption: null,
        paymentOption: null,
        shippingFullName: "",
        secondAddressRow: "",
        street: "",
        housenumber: "",
        plz: "",
        place: "",
      },
      orderedItems: {},
      shippingAddressFormValid: false,
    };
  },
};
</script>

<style>
.item-description p {
  margin-bottom: 4px;
}

.order-item-image {
  border-radius: 5px;
}

.order-item-fake-image {
  border-radius: 5px;
  width: 100%;
  padding-top: calc(50% - 40px);
  padding-bottom: calc(50% - 40px);
}

.order-item-count {
  width: 50px;
  text-align: center;
}
</style>
