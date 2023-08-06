Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.

`0.6`_ - 2023-05-28
-------------------

Nothing changed.

`0.5.1`_ - 2023-03-09
---------------------

Fixed
~~~~~

* Fix tracking of share expirations for digital products.

`0.5`_ - 2023-03-04
------------------

This version requires AlekSIS-Core 3.0. It is incompatible with any previous
version.

Removed
~~~~~~~

* Legacy menu integration for AlekSIS-Core pre-3.0

Added
~~~~~

* Add SPA support for AlekSIS-Core 3.0

`0.4.1`_ - 2023-03-09
---------------------

Added
~~~~~

* Special items (e. g. digital products) can now be excluded 
  from shipping cost calculation.
* Support digital products via Nextcloud.
* Items can be excluded from shipping cost calculation (e. g. digital products).

Changed
~~~~~~~

* Introduce new Vue(tify) frontend for order form.
* Divide processing options into shipping and payment options.
* Items now can be ordered in the form.

Fixed
~~~~~

* Label buttons in list view didn't work.
* Text-only emails contained too much whitespace.
* Make HTML mails compatible with more clients.
* Layout in order statistics table was broken.

`0.4`_ - 2022-06-09
-------------------

Added
~~~~~

* Implement special form as an easy way to manage pick up.

`0.3`_ - 2022-05-31
-------------------

Added
~~~~~

* Reminder emails for confirmation and payment.

`0.2`_ - 2022-05-01
-------------------

Added
~~~~~

* Divide statistics by current order status.
* Add delete button for orders.

Changed
~~~~~~~

* Use top nav bar with tabs to switch between list and overview.
* Use Iconify icons instead of icon font.
* Directly render PDF for list and packing lists.

Fixed
~~~~~

* Full name search filter didn't work.
* The sum calculation in the actual order form didn't work and showed much too high numbers.
* PDF generation didn't work on most servers with correct file permissions.
* Add some space under buttons.

`0.1.1`_ - 2021-12-29
---------------------

Changed
~~~~~~~

* Update project files.

`0.1b0`_ - 2021-05-30
---------------------

Added
~~~~~
- Create order forms.
- Send order information via email.
- Manage order status.
- Generate reports, address and barcode labels.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

.. _0.1b0: https://edugit.org/hansegucker/AlekSIS-App-Order/-/tags/0.1b0
.. _0.1.1: https://edugit.org/hansegucker/AlekSIS-App-Order/-/tags/0.1.1
.. _0.2: https://edugit.org/hansegucker/AlekSIS-App-Order/-/tags/0.2
.. _0.3: https://edugit.org/hansegucker/AlekSIS-App-Order/-/tags/0.3
.. _0.4: https://edugit.org/hansegucker/AlekSIS-App-Order/-/tags/0.4
.. _0.4.1: https://edugit.org/hansegucker/AlekSIS-App-Order/-/tags/0.4.1
.. _0.5: https://edugit.org/hansegucker/AlekSIS-App-Order/-/tags/0.5
.. _0.5.1: https://edugit.org/hansegucker/AlekSIS-App-Order/-/tags/0.5.1
.. _0.6: https://edugit.org/hansegucker/AlekSIS-App-Order/-/tags/0.6
