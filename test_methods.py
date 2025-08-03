#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify all Kings Mobile Automation methods are properly accessible
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_method_accessibility():
    """Test that all previously missing methods are now accessible"""
    print("🧪 Testing Kings Mobile Automation Method Accessibility...")
    
    try:
        from kings_mobile_automation import KingsMobileAutomation
        
        # Create instance
        automation = KingsMobileAutomation()
        
        # Test previously missing methods
        methods_to_test = [
            'process_task_queue',
            'start_auto_troop_training', 
            'get_active_marches',
            'help_all_alliance',
            'auto_level_heroes',
            'start_resource_march',
            'collect_vip_chest',
            'collect_free_chests',
            'attack_dragon_lair',
            'collect_alliance_gifts',
            'complete_daily_quests',
            'auto_upgrade_equipment',
            'auto_allocate_talents',
            'start_auto_research',
            'start_auto_building_upgrade',
            'use_shield',
            'use_teleport',
            'start_building_upgrade',
            'start_troop_training',
            'start_research',
            'heal_all_troops',
            'extract_resource_amount',
            'extract_troop_count',
            'extract_war_info'
        ]
        
        print(f"📋 Testing {len(methods_to_test)} methods...")
        
        missing_methods = []
        accessible_methods = []
        
        for method_name in methods_to_test:
            if hasattr(automation, method_name):
                method = getattr(automation, method_name)
                if callable(method):
                    accessible_methods.append(method_name)
                    print(f"✅ {method_name} - ACCESSIBLE")
                else:
                    missing_methods.append(method_name)
                    print(f"❌ {method_name} - NOT CALLABLE")
            else:
                missing_methods.append(method_name)
                print(f"❌ {method_name} - NOT FOUND")
        
        print(f"\n📊 Test Results:")
        print(f"✅ Accessible Methods: {len(accessible_methods)}/{len(methods_to_test)}")
        print(f"❌ Missing Methods: {len(missing_methods)}")
        
        if missing_methods:
            print(f"\n🚨 Missing Methods:")
            for method in missing_methods:
                print(f"   - {method}")
            return False
        else:
            print(f"\n🎉 All methods are properly accessible!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_method_accessibility()
    if success:
        print("\n✅ Kings Mobile Automation methods test PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Kings Mobile Automation methods test FAILED!")
        sys.exit(1)
