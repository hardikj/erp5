section_value = context.getDestinationSectionValue()

if section_value is None or \
   section_value.getProperty('price_currency', None) is None:
  # If no section defined, no way to convert currencies
  return 0

transaction_currency = context.getResource()
if transaction_currency is not None and\
   transaction_currency != section_value.getProperty('price_currency', None):
  return 1

for line in context.getMovementList(
   portal_type=context.getPortalAccountingMovementTypeList()):
  if ((line.getDestinationCredit() !=
       line.getDestinationInventoriatedTotalAssetCredit()) or (
       line.getDestinationDebit() !=
       line.getDestinationInventoriatedTotalAssetDebit())):
   return 1

return 0
