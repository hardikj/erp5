request = context.REQUEST
source = context.getSource()
source_section = context.getSourceSection()

#cash_status = ['valid', 'new_emitted']
cash_status = ['valid']
#emission_letter = None
#emission_letter = list((context.getSourceValue().getCodification()[0]).lower())
emission_letter = context.Baobab_getUserEmissionLetterList()
context.log('emission_letter',emission_letter)
variation = context.Baobab_getResourceVintageList(banknote=1, coin=1)

cash_detail_dict = {'line_portal_type'           : 'Outgoing Cash To Currency Purchase Line'
                    , 'operation_currency'       : context.Baobab_getPortalReferenceCurrencyID()
                    , 'cash_status_list'         : cash_status
                    , 'emission_letter_list'     : emission_letter
                    , 'variation_list'           : variation
                    , 'currency_cash_portal_type': None
                    , 'read_only'                : False
                    , 'column_base_category'     : 'variation'
                    }

return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url()
                                                          , target_total_price = context.getQuantity()
                                                          )
