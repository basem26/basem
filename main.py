from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp

class SavingsCalculator(BoxLayout):
    initial_deposit = ObjectProperty(None)
    annual_interest = ObjectProperty(None)
    years = ObjectProperty(None)
    result_label = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        
        # Input fields
        self.initial_deposit = TextInput(hint_text='Initial Deposit ($)', multiline=False)
        self.annual_interest = TextInput(hint_text='Annual Interest Rate (%)', multiline=False)
        self.years = TextInput(hint_text='Number of Years', multiline=False)
        
        self.add_widget(self.initial_deposit)
        self.add_widget(self.annual_interest)
        self.add_widget(self.years)
        
        # Calculate button
        self.calculate_btn = Button(text='Calculate', size_hint_y=None, height=dp(50))
        self.calculate_btn.bind(on_press=self.start_calculation)
        self.add_widget(self.calculate_btn)
        
        # Result area
        self.results = ScrollView(size_hint=(1, 1))
        self.result_label = Label(
            text='', 
            size_hint_y=None, 
            halign='left', 
            valign='top',
            markup=True
        )
        self.result_label.bind(texture_size=self.update_label_size)
        self.results.add_widget(self.result_label)
        self.add_widget(self.results)
        
        # Calculation variables
        self.calculation_data = None
        self.current_year = 1

    def update_label_size(self, instance, size):
        instance.size = (size[0], size[1] + dp(20))
        instance.text_size = (size[0], None)

    def start_calculation(self, instance):
        try:
            initial = float(self.initial_deposit.text)
            rate = float(self.annual_interest.text)
            years = int(self.years.text)
            
            self.calculation_data = {
                'current_balance': initial,
                'annual_rate': rate,
                'years': years,
                'results': [],
                'original_rate': rate,
                'original_deposit': initial
            }
            
            self.result_label.text = ''
            self.current_year = 1
            Clock.schedule_once(lambda dt: self.calculate_year(), 0.1)
            
        except Exception as e:
            self.show_error(str(e))

    def calculate_year(self):
        if self.current_year > 1:
            self.show_year_popup()
        else:
            self.process_year()

    def show_year_popup(self):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        popup = Popup(title=f'Year {self.current_year} Adjustments', content=content,
                     size_hint=(0.8, 0.4), auto_dismiss=False)
        
        rate_input = TextInput(hint_text=f'New Rate (current: {self.calculation_data["annual_rate"]}%)', 
                             multiline=False)
        deposit_input = TextInput(hint_text='Additional Deposit ($)', multiline=False)
        
        content.add_widget(rate_input)
        content.add_widget(deposit_input)
        
        def process_input(instance):
            try:
                if rate_input.text.strip():
                    new_rate = float(rate_input.text)
                    if new_rate >= 0:
                        self.calculation_data['annual_rate'] = new_rate
                
                deposit = float(deposit_input.text or 0)
                if deposit >= 0:
                    self.calculation_data['current_balance'] += deposit
                
                popup.dismiss()
                Clock.schedule_once(lambda dt: self.process_year(), 0.1)
                
            except ValueError:
                self.show_error("Invalid input values")
        
        btn = Button(text='Continue', size_hint_y=None, height=dp(50))
        btn.bind(on_press=process_input)
        content.add_widget(btn)
        
        popup.open()

    def process_year(self):
        annual_rate_decimal = self.calculation_data['annual_rate'] / 100
        current_balance = self.calculation_data['current_balance']
        
        year_text = f"[b]Year {self.current_year}:[/b]\n"
        for month in range(1, 13):
            monthly_interest = current_balance * annual_rate_decimal / 12
            current_balance += monthly_interest
            self.calculation_data['results'].append((month + (self.current_year-1)*12, current_balance))
            year_text += f"Month {month + (self.current_year-1)*12:03}: ${current_balance:,.2f}\n"
        
        self.calculation_data['current_balance'] = current_balance
        self.result_label.text += year_text + "\n"
        
        if self.current_year < self.calculation_data['years']:
            self.current_year += 1
            Clock.schedule_once(lambda dt: self.calculate_year(), 0.1)
        else:
            self.show_final_results()

    def show_final_results(self):
        final_text = "\n[b]Final Report:[/b]\n"
        final_text += f"Initial Deposit: ${self.calculation_data['original_deposit']:,.2f}\n"
        final_text += f"Final Balance: ${self.calculation_data['current_balance']:,.2f}\n"
        self.result_label.text += final_text

    def show_error(self, message):
        content = Label(text=message)
        popup = Popup(title='Error', content=content,
                     size_hint=(0.8, 0.4), auto_dismiss=True)
        popup.open()

class SavingsApp(App):
    def build(self):
        return SavingsCalculator()

if __name__ == '__main__':
    SavingsApp().run()